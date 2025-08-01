import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

def generate_lessons(skill_slug, mode="continue", minutes=20, previous_content=None):
    prompt = f"Generate {minutes}-minute learning lessons for the skill '{skill_slug}' in {mode} mode. Format: Each lesson as a separate line."
    response = model.generate_content(prompt)
    return response.text.strip().split("\n")

def generate_flashcards(skill_slug):
    prompt = f"Create 5 flashcards for the skill: {skill_slug}. Format: Question | Answer (separated by '|')."
    response = model.generate_content(prompt)
    cards = []
    for line in response.text.strip().split("\n"):
        if '|' in line:
            q, a = line.split('|', 1)
            cards.append({'question': q.strip(), 'answer': a.strip()})
    return cards

def generate_quizzes(skill_slug):
    prompt = f"Create 5 multiple choice quiz questions for the skill: {skill_slug}. Format: Question, then A) Option, B) Option, C) Option, D) Option, then Answer: (A/B/C/D). Separate each question by a blank line."
    response = model.generate_content(prompt)
    quizzes = []
    for block in response.text.strip().split('\n\n'):
        lines = block.strip().split('\n')
        if len(lines) >= 6:
            question = lines[0]
            options = [l[3:].strip() for l in lines[1:5]]
            answer_line = lines[5]
            answer = answer_line.split(':')[-1].strip()
            quizzes.append({'question': question, 'options': options, 'answer': answer})
    return quizzes

def calculate_xp(mode="continue", minutes=20):
    return min(50, 5 + (minutes * 2 if mode == "continue" else minutes))
