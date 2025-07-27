from django.conf import settings
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    xp_total = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    weekly_progress_pct = models.PositiveSmallIntegerField(default=0)
    active_skills_count = models.PositiveSmallIntegerField(default=0)
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

    class Meta:
        unique_together = ("user", "skill")

    def __str__(self):
        return f"{self.user.username} - {self.skill.title} ({'active' if self.is_active else 'inactive'})"


class Activity(models.Model):
    # Suggested types (you can add more freely)
    LESSON_COMPLETED = "lesson_completed"
    QUIZ_ATTEMPTED = "quiz_attempted"
    XP_AWARDED = "xp_awarded"
    STREAK_UPDATED = "streak_updated"
    SKILL_STARTED = "skill_started"
    SKILL_COMPLETED = "skill_completed"

    TYPE_CHOICES = (
        (LESSON_COMPLETED, "Lesson Completed"),
        (QUIZ_ATTEMPTED, "Quiz Attempted"),
        (XP_AWARDED, "XP Awarded"),
        (STREAK_UPDATED, "Streak Updated"),
        (SKILL_STARTED, "Skill Started"),
        (SKILL_COMPLETED, "Skill Completed"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activities")
    skill = models.ForeignKey(Skill, null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    xp_delta = models.IntegerField(default=0)
    payload = models.JSONField(default=dict, blank=True)  # flexible: quiz score, lesson id, answers, etc.
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.username} - {self.type} ({self.xp_delta:+}) @ {self.created_at:%Y-%m-%d %H:%M}"


class QuizAttempt(models.Model):  # Optional but handy to query attempts directly
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
    skill = models.ForeignKey(Skill, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200)
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    answers_json = models.JSONField(default=dict, blank=True)

    def duration_seconds(self):
        if self.finished_at:
            return int((self.finished_at - self.started_at).total_seconds())
        return 0

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.score}/{self.max_score})"
