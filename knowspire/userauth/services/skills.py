# userauth/services/skills.py

from datetime import date
from django.db import transaction
from django.utils import timezone

from userauth.models import (
    Skill,
    UserSkill,
)

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
