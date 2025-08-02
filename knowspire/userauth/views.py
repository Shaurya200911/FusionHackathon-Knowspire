from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from .models import UserProfile, Skill, UserSkill
from django.db import IntegrityError, transaction
from django.db import connection
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .services import gemini
from django.core.cache import cache
import json

# Login

def login_view(request):
    if request.user.is_authenticated:
        return redirect('paywall')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('paywall')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html', {'form': form})

# Index

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
        return render(request, 'index.html')
    return render(request, 'index.html')

# Register

def register_view(request):
    if request.user.is_authenticated:
        return redirect('paywall')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('paywall')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

# Paywall

@login_required
def paywall_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'paywall.html')

# Dashboard

@login_required
def dashboard_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    # Calculate weekly progress: percent of days with activity in last 7 days
    today = timezone.now().date()
    last_7_days = [today - timezone.timedelta(days=i) for i in range(7)]
    streak_days = set()
    if profile.last_activity_at:
        for i in range(profile.current_streak):
            streak_days.add((profile.last_activity_at.date() - timezone.timedelta(days=i)))
    weekly_progress = int(100 * len(set(last_7_days) & streak_days) / 7)

    # Recent activity: skill added or streak continued
    activities = []
    # Skill added (last 5)
    new_skills = UserSkill.objects.filter(user=request.user).order_by('-started_at')[:5]
    for skill in new_skills:
        activities.append(f"Added skill: {skill.skill.title}")
    # Streak continued (today)
    if profile.last_activity_at and profile.last_activity_at.date() == today:
        activities.insert(0, f"Streak continued! ({profile.current_streak} days)")
    else:
        activities.insert(0, "No streak today.")
    context = {
        "profile": profile,
        "xp": profile.xp_total,
        "streak": profile.current_streak,
        "longest_streak": profile.longest_streak,
        "skills_count": UserSkill.objects.filter(user=request.user, is_active=True).count(),
        "weekly_progress": weekly_progress,
        "activity_history": activities,
        "last_seen": profile.last_activity_at,
        "today": today,
    }
    return render(request, "dashboard.html", context)

# Leaderboard

@login_required
def leaderboard_view(request):
    profiles = UserProfile.objects.select_related("user").order_by("-xp_total")
    leaderboard = [
        {
            "user": profile.user,
            "xp_total": profile.xp_total,
            "current_streak": profile.current_streak
        }
        for profile in profiles
    ]
    return render(request, 'leaderboard.html', {
        "top_users": leaderboard,
        "current_user": request.user
    })

# Skills

@login_required
def skills_view(request):
    user = request.user
    if request.method == "POST":
        skill_slug = request.POST.get("skill_slug")
        active_skill_count = UserSkill.objects.filter(user=user, is_active=True).count()
        if active_skill_count >= 3:
            messages.error(request, "You cannot have more than 3 active skills at a time. Please archive or delete an active skill before adding a new one.")
            return redirect("skills")
        if skill_slug:
            skill, _ = Skill.objects.get_or_create(slug=skill_slug, defaults={"title": skill_slug})
            user_skill, _ = UserSkill.objects.get_or_create(user=user, skill=skill)
            user_skill.is_active = True
            user_skill.save()
            messages.success(request, f"Skill '{user_skill.skill.title}' started!")
            return redirect("skills")
    active_user_skills = UserSkill.objects.filter(user=user, is_active=True).select_related("skill")
    archived_user_skills = UserSkill.objects.filter(user=user, is_active=False).select_related("skill")
    all_skills = Skill.objects.all()
    return render(request, "skills.html", {
        "active_user_skills": active_user_skills,
        "archived_user_skills": archived_user_skills,
        "available_skills": all_skills
    })

@login_required
def start_skill_view(request):
    if request.method == "POST":
        slug = request.POST.get("skill_slug")
        skill, _ = Skill.objects.get_or_create(slug=slug, defaults={"title": slug})
        user_skill, _ = UserSkill.objects.get_or_create(user=request.user, skill=skill)
        user_skill.is_active = True
        user_skill.save()
        messages.success(request, "Skill activated successfully.")
    return redirect("skills")


@login_required
@csrf_exempt
def skill_detail_view(request, slug):
    skill = get_object_or_404(Skill, slug=slug)
    user_skill = get_object_or_404(UserSkill, user=request.user, skill=skill)
    user_profile = request.user.profile
    today = timezone.now().date()

    # XP limits and pacing
    MAX_XP_LESSONS = 150
    MAX_XP_COMPLETION = 50
    TOTAL_XP_SKILL = MAX_XP_LESSONS + MAX_XP_COMPLETION

    cache_key = f"session_content_{request.user.id}_{skill.slug}"
    session_content = cache.get(cache_key)

    # Only generate new content on POST (continue button)
    if request.method == "POST":
        # Doubt mode AJAX
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body)
                if data.get('doubt_mode'):
                    previous_content = (session_content.get('lessons', []) if session_content else []) + \
                                      (session_content.get('flashcards', []) if session_content else []) + \
                                      (session_content.get('quizzes', []) if session_content else [])
                    previous_text = '\n'.join([str(x) for x in previous_content])
                    answer = gemini.answer_doubt(skill.slug, previous_text, data.get('doubt', ''))
                    return HttpResponse(json.dumps({'answer': answer}), content_type='application/json')
            except Exception:
                return HttpResponse(json.dumps({'answer': 'Error processing doubt.'}), content_type='application/json')
        # Quiz/flashcard submission
        elif 'quiz-submit' in request.POST:
            quizzes = session_content.get('quizzes', gemini.generate_quizzes(skill.slug)) if session_content else []
            correct_count = 0
            for i, quiz in enumerate(quizzes):
                user_answer = request.POST.get(f'quiz-{i}')
                if user_answer and user_answer.strip().upper() == quiz['answer'].upper():
                    correct_count += 1
            xp_gain = correct_count * XP_QUIZ_CORRECT
            xp_possible = MAX_XP_TOTAL - user_profile.xp_total
            xp_gain = min(xp_gain, xp_possible)
            user_profile.xp_total += xp_gain
            user_profile.save()
            messages.success(request, f"You got {correct_count} correct! +{xp_gain} XP.")
            lessons = session_content.get('lessons', []) if session_content else []
            flashcards = session_content.get('flashcards', []) if session_content else []
            return render(request, "skill_detail.html", {
                "skill": skill,
                "lessons": lessons,
                "flashcards": flashcards,
                "quizzes": quizzes,
                "session_started": True
            })
        elif 'flashcard-submit' in request.POST:
            xp_possible = MAX_XP_TOTAL - user_profile.xp_total
            xp_gain = min(XP_FLASHCARD, xp_possible)
            user_profile.xp_total += xp_gain
            user_profile.save()
            messages.success(request, f"Flashcards completed! +{xp_gain} XP.")
            lessons = session_content.get('lessons', []) if session_content else []
            flashcards = session_content.get('flashcards', []) if session_content else []
            quizzes = session_content.get('quizzes', []) if session_content else []
            return render(request, "skill_detail.html", {
                "skill": skill,
                "lessons": lessons,
                "flashcards": flashcards,
                "quizzes": quizzes,
                "session_started": True
            })
        else:
            session_time = int(request.POST.get("session-time", 20))
            session_mode = request.POST.get("session-mode", "continue")
            if user_skill.total_minutes_spent + session_time > 1500:
                messages.warning(request, "You've reached the 25-hour limit for this skill.")
                return render(request, "skill_detail.html", {
                    "skill": skill,
                    "limit_reached": True
                })
            # Gather previous content for context
            previous_lessons = user_skill.lessons_cache or ""
            previous_flashcards = user_skill.flashcards_cache or ""
            previous_quizzes = user_skill.quizzes_cache or ""
            previous_content = f"{previous_lessons}\n{previous_flashcards}\n{previous_quizzes}"
            lessons = gemini.generate_lessons(skill.slug, session_mode, session_time, previous_content)
            flashcards = gemini.generate_flashcards(skill.slug, previous_content, session_mode)
            quizzes = gemini.generate_quizzes(skill.slug, previous_content, session_mode)
            session_content = {
                'lessons': lessons,
                'flashcards': flashcards,
                'quizzes': quizzes
            }
            cache.set(cache_key, session_content, timeout=60*60*24)  # 1 day
            # XP pacing: percent progress
            percent_progress = min(100, ((user_skill.total_minutes_spent + session_time) / 1500) * 100)
            xp_gain = int((percent_progress / 100) * MAX_XP_LESSONS) - user_skill.xp_earned
            xp_gain = max(0, xp_gain)
            user_profile.xp_total += xp_gain
            user_profile.save()
            user_skill.total_minutes_spent += session_time
            user_skill.xp_earned += xp_gain
            # Completion bonus
            if percent_progress == 100 and not user_skill.completed_at:
                user_profile.xp_total += MAX_XP_COMPLETION
                user_profile.save()
                user_skill.completed_at = timezone.now()
            user_skill.save()
            return render(request, "skill_detail.html", {
                "skill": skill,
                "lessons": lessons,
                "flashcards": flashcards,
                "quizzes": quizzes,
                "session_started": True
            })
    # On GET, show last session content if available
    if session_content:
        return render(request, "skill_detail.html", {
            "skill": skill,
            "lessons": session_content.get('lessons', []),
            "flashcards": session_content.get('flashcards', []),
            "quizzes": session_content.get('quizzes', []),
            "session_started": True
        })
    return render(request, "skill_detail.html", {
        "skill": skill
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
        try:
            with transaction.atomic():
                cursor = connection.cursor()
                # Clean up legacy/related tables for this user_skill
                for table in ["flashcard", "quiz", "lessonitem"]:
                    try:
                        cursor.execute(f"DELETE FROM {table} WHERE user_skill_id = %s", [user_skill_id])
                    except Exception:
                        pass
                # Delete the user_skill
                user_skill.delete()
                # If there are no more UserSkills for this skill, delete the Skill itself
                if not UserSkill.objects.filter(skill=user_skill.skill).exists():
                    user_skill.skill.delete()
            messages.success(request, f"Skill '{skill_title}' deleted.")
        except IntegrityError:
            messages.error(request, f"Could not delete skill '{skill_title}' due to related data. Please contact support or clean up related data.")
    return redirect("skills")

@login_required
def download_skill_data(request, user_skill_id):
    user_skill = get_object_or_404(UserSkill, id=user_skill_id, user=request.user)
    data = {
        "skill": user_skill.skill.title,
        "flashcards": [],
        "quizzes": []
    }
    response = HttpResponse(json.dumps(data, indent=2), content_type="application/json")
    filename = f"{user_skill.skill.slug}_data.json"
    response["Content-Disposition"] = f"attachment; filename={filename}"
    return response

def logout_view(request):
    logout(request)
    return redirect("home")
