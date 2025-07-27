# userauth/signals.py
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile

from .models import UserProfile, Activity, UserSkill


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=UserSkill)
def update_active_skills_count(sender, instance, **kwargs):
    # keep the counter in sync for fast checks
    profile = instance.user.profile
    active_count = UserSkill.objects.filter(user=instance.user, is_active=True).count()
    if profile.active_skills_count != active_count:
        profile.active_skills_count = active_count
        profile.save(update_fields=["active_skills_count"])


@receiver(post_save, sender=Activity)
def update_profile_from_activity(sender, instance: Activity, created, **kwargs):
    if not created:
        return

    profile = instance.user.profile
    # XP
    if instance.xp_delta:
        profile.xp_total = (profile.xp_total or 0) + instance.xp_delta

    # Streaks: bump/reset depending on days difference
    now = timezone.now()
    today = now.date()
    last_dt = profile.last_activity_at
    if last_dt is None:
        # first ever activity
        profile.current_streak = 1
        profile.longest_streak = max(profile.longest_streak, profile.current_streak)
    else:
        last_day = last_dt.date()
        if last_day == today:
            # same day, streak unchanged
            pass
        elif (today - last_day).days == 1:
            # consecutive day
            profile.current_streak += 1
            if profile.current_streak > profile.longest_streak:
                profile.longest_streak = profile.current_streak
        else:
            # broke streak
            profile.current_streak = 1

    profile.last_activity_at = now
    profile.save(update_fields=["xp_total", "current_streak", "longest_streak", "last_activity_at"])

