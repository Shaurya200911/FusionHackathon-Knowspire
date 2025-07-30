from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from .forms import ContactForm
from django.contrib import messages
from django.db.models import Q
from datetime import date
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.models import User
from .models import XPLog, UserProfile
from .services.xp_log import award_quiz_xp
from .models import Skill
from django.shortcuts import get_object_or_404
from .services.start_skill import start_skill
from .models import Activity, UserSkill, UserProfile, Skill
from .services.streaks import apply_daily_streak
from .services.skills import ensure_today_content
import json

# Create your views here.


def login_view(request):
    if request.user.is_authenticated:
        return redirect('paywall')  # Redirect to paywall if already logged in

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('paywall')  # Go to paywall
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {'form': form})



def index_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        send_mail(
            subject=f"Message from {name}",
            message=f"From: {name} <{email}>\n\n{message}",
            from_email=email,
            recipient_list=['skc112009@gmail.com'],
        )
        messages.success(request, 'Message sent successfully!')
        return render(request, 'index.html')  # Optional: keep user on same section
    return render(request, 'index.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('paywall')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('paywall')  # Go to paywall
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


@login_required
def paywall_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'paywall.html')


@login_required
def dashboard_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    recent_activities = (
        Activity.objects
        .filter(user=request.user)
        .select_related("skill")
        .order_by('-created_at')[:5]
    )

    def render_activity(a):
        # Build one nice, human-readable line per activity
        xp_part = f" (+{a.xp_delta} XP)" if a.xp_delta else ""
        if a.type == Activity.QUIZ_ATTEMPTED:
            title = a.payload.get("quiz_title", "(untitled)")
            score = a.payload.get("score", "-")
            max_score = a.payload.get("max_score", "-")
            return f'🧠 Quiz "{title}" – {score}/{max_score}{xp_part}'
        elif a.type == Activity.LESSON_COMPLETED:
            lesson_title = a.payload.get("lesson_title", "(unknown)")
            return f'📘 Lesson "{lesson_title}" completed{xp_part}'
        elif a.type == Activity.SKILL_STARTED:
            skill_title = a.skill.title if a.skill else "(unknown skill)"
            return f'🚀 Started skill "{skill_title}"'
        elif a.type == Activity.SKILL_COMPLETED:
            skill_title = a.skill.title if a.skill else "(unknown skill)"
            return f'🏁 Completed skill "{skill_title}"{xp_part}'
        elif a.type == Activity.STREAK_UPDATED:
            return f'🔥 Streak updated to {profile.current_streak} days'
        else:
            # generic
            return f'{a.get_type_display()}{xp_part}'

    activities_ui = [
        {"text": render_activity(a), "when": a.created_at}
        for a in recent_activities
    ]

    context = {
        "profile": profile,
        "xp": profile.xp_total,
        "streak": profile.current_streak,
        "longest_streak": profile.longest_streak,
        "skills_count": UserSkill.objects.filter(user=request.user, is_active=True).count(),
        "weekly_progress": profile.weekly_progress_pct or 0,
        "recent_activities_ui": activities_ui,
        "last_seen": profile.last_activity_at,
        "today": timezone.now().date(),
    }
    return render(request, "dashboard.html", context)

@login_required
def leaderboard_view(request):
    # Annotate total XP from XPLog
    user_xp_data = (
        XPLog.objects
        .values('user')
        .annotate(total_xp=Sum('xp_amount'))
        .order_by('-total_xp')[:50]
    )

    # Get user objects and profiles
    user_ids = [entry['user'] for entry in user_xp_data]
    users = User.objects.in_bulk(user_ids)
    profiles = UserProfile.objects.in_bulk(user_ids)

    # Join into final leaderboard list
    leaderboard = []
    for entry in user_xp_data:
        user = users.get(entry['user'])
        profile = profiles.get(entry['user'])
        if user and profile:
            leaderboard.append({
                "user": user,
                "xp_total": entry['total_xp'],
                "current_streak": profile.current_streak
            })

    return render(request, 'leaderboard.html', {
        "top_users": leaderboard,
        "current_user": request.user
    })


@login_required
def skills_view(request):
    user = request.user

    if request.method == "POST":
        skill_slug = request.POST.get("skill_slug")
        if skill_slug:
            user_skill, error = start_skill(user, skill_slug)
            if error:
                messages.error(request, error)
            else:
                messages.success(request, f"Skill '{user_skill.skill.title}' started!")
            return redirect("skills")

    active_user_skills = UserSkill.objects.filter(user=user, is_active=True).select_related("skill")
    archived_user_skills = UserSkill.objects.filter(user=user, is_active=False).select_related("skill")

    # 🔹 Pass all skills so we can auto-fill the datalist
    all_skills = Skill.objects.all()

    return render(request, "skills.html", {
        "active_user_skills": active_user_skills,
        "archived_user_skills": archived_user_skills,
        "available_skills": all_skills  # important
    })
@login_required
def start_skill_view(request):
    if request.method == "POST":
        slug = request.POST.get("skill_slug")
        try:
            start_skill(request.user, slug)
            messages.success(request, "Skill activated successfully.")
        except Exception as e:
            messages.error(request, f"Could not activate skill: {e}")
    return redirect("skills")


@login_required
def skill_detail_view(request, slug):
    user = request.user
    today = timezone.now().date()

    # Get skill
    skill = get_object_or_404(Skill, slug=slug)

    # Get user's skill instance
    user_skill = get_object_or_404(UserSkill, user=user, skill=skill)

    # Redirect if skill is archived
    if not user_skill.is_active:
        return redirect("skills")

    # Ensure today’s flashcard and quiz are created or reused
    flashcard, quiz = ensure_today_content(user_skill, today)

    # Prepare quiz options as list for template (required for Django templates)
    options = [
        quiz.option_1,
        quiz.option_2,
        quiz.option_3,
        quiz.option_4
    ]

    return render(request, "skill_detail.html", {
        "skill": skill,
        "user_skill": user_skill,
        "flashcard": flashcard,
        "quiz": quiz,
        "options": options
    })
# views.py
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Quiz, QuizAttempt, XPLog, UserSkill

@require_POST
@login_required
def submit_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user = request.user
    answer = request.POST.get('answer')

    # Prevent re-submission
    if QuizAttempt.objects.filter(user=user, quiz=quiz).exists():
        return JsonResponse({"status": "error", "message": "Already attempted."})

    is_correct = (answer == quiz.correct_answer)

    # Log attempt
    QuizAttempt.objects.create(
        user=user,
        quiz=quiz,
        selected_answer=answer,
        is_correct=is_correct
    )

    # Award XP and update progress if correct
    if is_correct:
        user_skill = quiz.user_skill
        user_skill.xp_earned += 5
        user_skill.progress_pct += 5  # optional logic
        user_skill.save()

        XPLog.objects.create(
            user=user,
            skill=user_skill.skill,
            xp_amount=5,
            reason="Quiz Correct",
        )

    return JsonResponse({
        "status": "success",
        "is_correct": is_correct,
        "correct_answer": quiz.correct_answer,
        "xp_awarded": 5 if is_correct else 0
    })

@login_required
def archive_skill(request, user_skill_id):
    if request.method == "POST":
        user_skill = get_object_or_404(UserSkill, id=user_skill_id, user=request.user)
        user_skill.is_active = False
        user_skill.save()
        messages.success(request, f"Skill '{user_skill.skill.title}' archived.")
    return redirect("skills")

@login_required
def delete_skill(request, user_skill_id):
    if request.method == "POST":
        user_skill = get_object_or_404(UserSkill, id=user_skill_id, user=request.user)
        skill_title = user_skill.skill.title
        user_skill.delete()
        messages.success(request, f"Skill '{skill_title}' deleted.")
    return redirect("skills")

@login_required
def download_skill_data(request, user_skill_id):
    user_skill = get_object_or_404(UserSkill, id=user_skill_id, user=request.user)

    flashcards = Flashcard.objects.filter(user_skill=user_skill)
    quizzes = Quiz.objects.filter(user_skill=user_skill)

    data = {
        "skill": user_skill.skill.title,
        "flashcards": [
            {"front": fc.front_text, "back": fc.back_text}
            for fc in flashcards
        ],
        "quizzes": [
            {
                "question": q.question_text,
                "options": [q.option_1, q.option_2, q.option_3, q.option_4],
                "correct": q.correct_answer
            }
            for q in quizzes
        ]
    }

    response = HttpResponse(json.dumps(data, indent=2), content_type="application/json")
    filename = f"{user_skill.skill.slug}_data.json"
    response["Content-Disposition"] = f"attachment; filename={filename}"
    return response