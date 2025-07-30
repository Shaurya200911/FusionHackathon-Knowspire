from django.utils.text import slugify
from ..models import Skill, UserSkill, Activity
from django.utils import timezone


def start_skill(user, skill_slug_or_title):
    slug = slugify(skill_slug_or_title)

    skill, _ = Skill.objects.get_or_create(
        slug=slug,
        defaults={"title": skill_slug_or_title.strip().title()}
    )

    # ✅ Prevent starting more than 3 skills
    active_count = UserSkill.objects.filter(user=user, is_active=True).count()
    if active_count >= 3:
        return None, "You’ve already started 3 active skills. Please archive one to continue."

    user_skill, created = UserSkill.objects.get_or_create(
        user=user,
        skill=skill,
        defaults={
            "started_at": timezone.now(),
            "is_active": True
        }
    )

    if not created and not user_skill.is_active:
        user_skill.is_active = True
        user_skill.save()
    elif not created:
        return user_skill, "You’ve already started this skill."

    Activity.objects.create(
        user=user,
        skill=skill,
        type=Activity.SKILL_STARTED,
        xp_delta=0,
        payload={"source": "start_skill"}
    )

    return user_skill, None