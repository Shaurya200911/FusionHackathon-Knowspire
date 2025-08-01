import google.generativeai as genai
from django.conf import settings
from userauth.models import UserSkill

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

def generate_lessons(skill_slug, mode="continue", minutes=20, previous_content=None):
    context = "" if not previous_content else f"Previously covered: {previous_content}\n"
    prompt = (
        f"{context}Generate {minutes}-minute learning lessons for the skill '{skill_slug}' in {mode} mode. "
        "Format: Each lesson as a separate block, with explanation, examples, and summary only. "
        "Do NOT include greetings, introductions, or any text before the actual lesson content. "
        "Do NOT repeat concepts already covered unless mode is 'revision'. "
        "If mode is 'revision', review and reinforce previous concepts."
    )
    response = model.generate_content(prompt)
    lessons = [block.strip() for block in response.text.strip().split('\n\n') if block.strip()]
    return lessons

def generate_flashcards(skill_slug, previous_content=None, mode="continue"):
    context = "" if not previous_content else f"Previously covered: {previous_content}\n"
    prompt = (
        f"{context}Create 5 flashcards for the skill: {skill_slug}. "
        "Format: Question | Answer (separated by '|'). Each flashcard on a new line. "
        "Do NOT include greetings, introductions, or any text before the actual flashcards. "
        "Do NOT repeat concepts already covered unless mode is 'revision'. "
        "If mode is 'revision', review and reinforce previous concepts."
    )
    response = model.generate_content(prompt)
    cards = []
    for line in response.text.strip().split("\n"):
        if '|' in line:
            q, a = line.split('|', 1)
            cards.append({'question': q.strip(), 'answer': a.strip()})
    return cards

def generate_quizzes(skill_slug, previous_content=None, mode="continue"):
    context = "" if not previous_content else f"Previously covered: {previous_content}\n"
    prompt = (
        f"{context}Create 5 multiple choice quiz questions for the skill: {skill_slug}. "
        "Format: Question, then A) Option, B) Option, C) Option, D) Option, then Answer: (A/B/C/D). Separate each question by a blank line. "
        "Do NOT include greetings, introductions, or any text before the actual quiz questions. "
        "Do NOT repeat concepts already covered unless mode is 'revision'. "
        "If mode is 'revision', review and reinforce previous concepts."
    )
    response = model.generate_content(prompt)
    quizzes = []
    for block in response.text.strip().split('\n\n'):
        lines = [l for l in block.strip().split('\n') if l.strip()]
        if len(lines) >= 6:
            question = lines[0]
            options = [l[3:].strip() for l in lines[1:5]]
            answer_line = lines[5]
            answer = answer_line.split(':')[-1].strip()
            quizzes.append({'question': question, 'options': options, 'answer': answer})
    return quizzes

def answer_doubt(skill_slug, previous_content, doubt):
    prompt = (
        f"You are Knowspire AI. The user is learning '{skill_slug}'. "
        f"Here is the previous lesson/flashcard/quiz context: {previous_content}. "
        f"The user has a doubt: '{doubt}'. Please answer the doubt clearly and factually, in a friendly tone."
    )
    response = model.generate_content(prompt)
    return response.text.strip()

def calculate_xp(mode="continue", minutes=20):
    return min(50, 5 + (minutes * 2 if mode == "continue" else minutes))

def get_or_generate_lessons(user_skill, skill_slug, mode="continue", minutes=20, previous_content=None):
    if user_skill.lessons_cache:
        return [block.strip() for block in user_skill.lessons_cache.strip().split('\n\n') if block.strip()]
    lessons = generate_lessons(skill_slug, mode, minutes, previous_content)
    user_skill.lessons_cache = '\n\n'.join(lessons)
    user_skill.save(update_fields=["lessons_cache"])
    return lessons

def get_or_generate_flashcards(user_skill, skill_slug):
    if user_skill.flashcards_cache:
        cards = []
        for line in user_skill.flashcards_cache.strip().split("\n"):
            if '|' in line:
                q, a = line.split('|', 1)
                cards.append({'question': q.strip(), 'answer': a.strip()})
        return cards
    cards = generate_flashcards(skill_slug)
    user_skill.flashcards_cache = '\n'.join([f"{c['question']} | {c['answer']}" for c in cards])
    user_skill.save(update_fields=["flashcards_cache"])
    return cards

def get_or_generate_quizzes(user_skill, skill_slug):
    if user_skill.quizzes_cache:
        quizzes = []
        for block in user_skill.quizzes_cache.strip().split('\n\n'):
            lines = [l for l in block.strip().split('\n') if l.strip()]
            if len(lines) >= 6:
                question = lines[0]
                options = [l[3:].strip() for l in lines[1:5]]
                answer_line = lines[5]
                answer = answer_line.split(':')[-1].strip()
                quizzes.append({'question': question, 'options': options, 'answer': answer})
        return quizzes
    quizzes = generate_quizzes(skill_slug)
    quiz_blocks = []
    for q in quizzes:
        block = f"{q['question']}\nA) {q['options'][0]}\nB) {q['options'][1]}\nC) {q['options'][2]}\nD) {q['options'][3]}\nAnswer: {q['answer']}"
        quiz_blocks.append(block)
    user_skill.quizzes_cache = '\n\n'.join(quiz_blocks)
    user_skill.save(update_fields=["quizzes_cache"])
    return quizzes
