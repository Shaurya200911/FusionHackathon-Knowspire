# userauth/services/skills.py

from datetime import date
from django.db import transaction
from django.utils import timezone

from userauth.models import (
    Activity,
    Skill,
    UserSkill,
    QuizAttempt,
)

# --------------------------------------------
# 🔹 Activity & XP Management Utilities
# --------------------------------------------

def log_activity(*, user, type, xp_delta=0, skill=None, payload=None):
    if payload is None:
        payload = {}
    return Activity.objects.create(
        user=user,
        skill=skill,
        type=type,
        xp_delta=xp_delta,
        payload=payload,
    )

@transaction.atomic
def award_xp(user, amount, *, skill=None, source="generic", extra=None):
    if extra is None:
        extra = {}
    extra["source"] = source
    return log_activity(user=user, type=Activity.XP_AWARDED, skill=skill, xp_delta=amount, payload=extra)


# --------------------------------------------
# 🔹 Skill Completion Handler
# --------------------------------------------

@transaction.atomic
def complete_skill(user, skill_slug):
    try:
        skill = Skill.objects.get(slug=skill_slug)
        us = UserSkill.objects.get(user=user, skill=skill)
    except (Skill.DoesNotExist, UserSkill.DoesNotExist):
        raise ValueError("Skill or UserSkill not found")

    us.is_active = False
    us.completed_at = timezone.now()
    us.progress_pct = 100
    us.save()

    log_activity(user=user, type=Activity.SKILL_COMPLETED, skill=skill, payload={"skill": skill.slug})


# --------------------------------------------
# 🔹 Content Generation Utilities (No API)
# --------------------------------------------

# All content generation and retrieval logic removed.
# Placeholder functions for future implementation.

def generate_content_if_needed(user_skill):
    """
    Placeholder: Content generation is disabled.
    """
    return None
