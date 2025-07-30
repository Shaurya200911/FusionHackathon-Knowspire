# userauth/services/skills.py

from datetime import date
import json
import requests
from django.db import transaction
from django.utils import timezone

from userauth.models import (
    Flashcard,
    Quiz,
    Activity,
    Skill,
    UserSkill,
    QuizAttempt
)
from .secrets import GEMINI_API_KEY

# ---------------------------
# 🔹 Gemini Prompt and API Call
# ---------------------------

def build_gemini_prompt(skill_title):
    return f"""
You are an educational content generator.

Create exactly ONE flashcard and ONE multiple-choice quiz for the skill: "{skill_title}"

Output JSON in the following format:
{{
  "flashcard": {{
    "front_text": "string",
    "back_text": "string"
  }},
  "quiz": {{
    "question_text": "string",
    "option_1": "string",
    "option_2": "string",
    "option_3": "string",
    "option_4": "string",
    "correct_answer": "string"
  }}
}}
Keep the flashcard and quiz simple, clear, and beginner-friendly.
"""


def call_gemini(skill_title):
    prompt = build_gemini_prompt(skill_title)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    response = requests.post(url, headers=headers, json=payload)

    try:
        result = response.json()
        content_text = result["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(content_text)
    except Exception as e:
        print("[Gemini Error]", e)
        return None


# ---------------------------
# 🔹 Content Generator for Flashcards + Quiz
# ---------------------------

def ensure_today_content(user_skill, today):
    # Already exists?
    try:
        flashcard = Flashcard.objects.get(user_skill=user_skill, created_on=today)
        quiz = Quiz.objects.get(user_skill=user_skill, created_on=today)
        return flashcard, quiz
    except Flashcard.DoesNotExist:
        pass
    except Quiz.DoesNotExist:
        pass

    # Call Gemini
    content = call_gemini(user_skill.skill.title)

    if content:
        flashcard = Flashcard.objects.create(
            user_skill=user_skill,
            front_text=content["flashcard"]["front_text"],
            back_text=content["flashcard"]["back_text"],
            created_on=today
        )
        quiz = Quiz.objects.create(
            user_skill=user_skill,
            question_text=content["quiz"]["question_text"],
            option_1=content["quiz"]["option_1"],
            option_2=content["quiz"]["option_2"],
            option_3=content["quiz"]["option_3"],
            option_4=content["quiz"]["option_4"],
            correct_answer=content["quiz"]["correct_answer"],
            created_on=today
        )
    else:
        # fallback dummy content
        flashcard = Flashcard.objects.create(
            user_skill=user_skill,
            front_text="Fallback term",
            back_text="This is a fallback definition due to an API issue.",
            created_on=today
        )
        quiz = Quiz.objects.create(
            user_skill=user_skill,
            question_text="What is the capital of France?",
            option_1="Berlin",
            option_2="Madrid",
            option_3="Paris",
            option_4="Rome",
            correct_answer="Paris",
            created_on=today
        )

    return flashcard, quiz


# ---------------------------
# 🔹 Utility: Log Activity (if needed elsewhere)
# ---------------------------

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


# ---------------------------
# 🔹 Utility: Complete a Skill (archive it)
# ---------------------------

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


# ---------------------------
# 🔹 Utility: Award XP (optional if not using XPLog)
# ---------------------------

@transaction.atomic
def award_xp(user, amount, *, skill=None, source="generic", extra=None):
    if extra is None:
        extra = {}
    extra["source"] = source
    return log_activity(user=user, type=Activity.XP_AWARDED, skill=skill, xp_delta=amount, payload=extra)
