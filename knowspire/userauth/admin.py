# userauth/admin.py
from django.contrib import admin
from .models import UserProfile, Skill, UserSkill, Activity, QuizAttempt


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "xp_total", "current_streak", "longest_streak", "active_skills_count", "weekly_progress_pct")
    search_fields = ("user__username", "user__email")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "slug")


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ("user", "skill", "is_active", "progress_pct", "xp_earned", "started_at", "completed_at")
    list_filter = ("is_active", "skill")
    search_fields = ("user__username", "skill__title")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "xp_delta", "skill", "created_at")
    list_filter = ("type", "skill")
    search_fields = ("user__username",)
    readonly_fields = ("payload",)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "score", "max_score", "passed", "started_at", "finished_at")
    search_fields = ("user__username", "title")
    list_filter = ("passed",)
    readonly_fields = ("answers_json",)
