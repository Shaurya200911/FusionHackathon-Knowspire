# userauth/signals.py
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile, UserSkill


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=UserSkill)
def update_active_skills_count(sender, instance, **kwargs):
    profile = instance.user.profile
    active_count = UserSkill.objects.filter(user=instance.user, is_active=True).count()
    # Only update if the field exists
    if hasattr(profile, "active_skills_count"):
        if profile.active_skills_count != active_count:
            profile.active_skills_count = active_count
            profile.save(update_fields=["active_skills_count"])
