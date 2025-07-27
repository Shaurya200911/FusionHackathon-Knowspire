# userauth/services.py
from django.utils import timezone
from django.db import transaction
from .models import Activity, Skill, UserSkill, QuizAttempt


def log_activity(*, user, type, xp_delta=0, skill=None, payload=None):
    """
    Create an activity row (the single source of truth).
    Signals will update the UserProfile automatically.
    """
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
def start_skill(user, skill_slug):
    try:
        skill = Skill.objects.get(slug=skill_slug, is_active=True)
    except Skill.DoesNotExist:
        raise ValueError("Skill not found or inactive")

    active_count = user.profile.active_skills_count  # maintained by signal
    if active_count >= 3:
        raise ValueError("You can only have 3 active skills at a time")

    us, created = UserSkill.objects.get_or_create(user=user, skill=skill)
    if not created and us.is_active:
        return us  # already active
    us.is_active = True
    us.started_at = timezone.now()
    us.save()

    log_activity(user=user, type=Activity.SKILL_STARTED, skill=skill, xp_delta=0, payload={"skill": skill.slug})
    return us


@transaction.atomic
def complete_skill(user, skill_slug):
    try:
        skill = Skill.objects.get(slug=skill_slug)
    except Skill.DoesNotExist:
        raise ValueError("Skill not found")

    try:
        us = UserSkill.objects.get(user=user, skill=skill)
    except UserSkill.DoesNotExist:
        raise ValueError("User is not enrolled in this skill")

    us.is_active = False
    us.completed_at = timezone.now()
    us.progress_pct = 100
    us.save()

    log_activity(user=user, type=Activity.SKILL_COMPLETED, skill=skill, payload={"skill": skill.slug})


def award_xp(user, amount, *, skill=None, source="generic", extra=None):
    if extra is None:
        extra = {}
    extra["source"] = source
    return log_activity(user=user, type=Activity.XP_AWARDED, skill=skill, xp_delta=amount, payload=extra)


@transaction.atomic
def record_quiz_attempt(user, *, skill=None, title, score, max_score, passed, answers_json):
    qa = QuizAttempt.objects.create(
        user=user,
        skill=skill,
        title=title,
        score=score,
        max_score=max_score,
        passed=passed,
        answers_json=answers_json,
        started_at=timezone.now(),
        finished_at=timezone.now(),
    )

    xp_gain = score  # simple rule; change however you want
    log_activity(
        user=user,
        type=Activity.QUIZ_ATTEMPTED,
        skill=skill,
        xp_delta=xp_gain,
        payload={
            "quiz_title": title,
            "score": score,
            "max_score": max_score,
            "passed": passed,
        },
    )
    return qa
