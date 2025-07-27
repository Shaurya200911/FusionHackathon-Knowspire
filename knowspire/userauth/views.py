from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from .forms import ContactForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from django.utils import timezone
from .models import Activity, UserSkill, UserProfile
from .services.streaks import apply_daily_streak

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
    apply_daily_streak(request.user)
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
    top_users = UserProfile.objects.select_related('user').order_by('-xp_total')[:50]
    return render(request, 'leaderboard.html', {
        'top_users': top_users,
        'current_user': request.user
    })