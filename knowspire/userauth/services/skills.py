# userauth/services/skills.py

from datetime import date
from django.db import transaction
from django.utils import timezone

from userauth.models import (
    Flashcard,
    Quiz,
    Activity,
    Skill,
    UserSkill,
    QuizAttempt,
    LessonItem,
    LearningSession,
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

def create_fallback_flashcard(user_skill, today):
    return Flashcard.objects.create(
        user_skill=user_skill,
        front_text="Fallback term",
        back_text="This is a fallback definition due to an API issue.",
        created_on=today
    )

def create_fallback_quiz(user_skill, today):
    return Quiz.objects.create(
        user_skill=user_skill,
        question_text="What is the capital of France?",
        option_1="Berlin",
        option_2="Madrid",
        option_3="Paris",
        option_4="Rome",
        correct_answer="Paris",
        created_on=today
    )


def generate_content_if_needed(user_skill):
    """
    Generate flashcards, quizzes, and lesson items for today if not already created.
    Returns the LearningSession object.
    """
    today = date.today()

    # Check if session exists
    session, created = LearningSession.objects.get_or_create(user_skill=user_skill, date=today)

    if created:
        # Nothing was created yet, use fallback content
        try:
            flashcard = create_fallback_flashcard(user_skill, today)
            quiz = create_fallback_quiz(user_skill, today)
        except Exception as e:
            print("[CONTENT GENERATION ERROR]:", e)
            # Optional: Log the error or mark the session as failed

    return session