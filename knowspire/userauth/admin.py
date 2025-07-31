# userauth/admin.py
from django.contrib import admin
from .models import UserProfile, Skill, UserSkill


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "xp_total", "current_streak", "longest_streak")
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
