from django.db import models
from django.conf import settings
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    xp_total = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"

class Skill(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class UserSkill(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    progress_pct = models.PositiveSmallIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_minutes_spent = models.PositiveIntegerField(default=0)
    # Add fields for cached Gemini content
    lessons_cache = models.TextField(blank=True, null=True)
    flashcards_cache = models.TextField(blank=True, null=True)
    quizzes_cache = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "skill")

    def __str__(self):
        return f"{self.user.username} - {self.skill.title} ({'active' if self.is_active else 'inactive'})"

class XPLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=True, blank=True)
    xp_amount = models.PositiveIntegerField()
    reason = models.CharField(max_length=120)
    awarded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.user.username}: +{self.xp_amount} XP for {self.reason} ({self.awarded_at:%Y-%m-%d %H:%M})"
