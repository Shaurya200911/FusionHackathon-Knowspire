# services/xp_log.py

from userauth.models import XPLog, UserSkill
from django.utils import timezone

def award_quiz_xp(user, skill, amount=5):
    user_skill, _ = UserSkill.objects.get_or_create(user=user, skill=skill)

    # Add to XPLog
    XPLog.objects.create(
        user=user,
        skill=skill,
        xp_amount=amount,
        reason="Quiz correct",
        awarded_at=timezone.now()
    )

    # Update UserSkill XP
    user_skill.xp += amount
    user.profile.xp_total += amount
    user_skill.save()

    # Optional: Update UserProfile XP if applicable
    if hasattr(user, 'profile'):
        user.profile.total_xp += amount
        user.profile.save()
