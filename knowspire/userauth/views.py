from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.utils import timezone
from .models import UserProfile, Skill, UserSkill
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
    context = {
        "profile": profile,
        "xp": profile.xp_total,
        "streak": profile.current_streak,
        "longest_streak": profile.longest_streak,
        "skills_count": UserSkill.objects.filter(user=request.user, is_active=True).count(),
        "weekly_progress": 0,  # No weekly_progress field anymore
        "recent_activities": [],  # No Activity model
        "last_seen": profile.last_activity_at,
        "today": timezone.now().date(),
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
def skill_detail_view(request, slug):
    skill = get_object_or_404(Skill, slug=slug)
    return render(request, "skill_detail.html", {"skill": skill})

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
