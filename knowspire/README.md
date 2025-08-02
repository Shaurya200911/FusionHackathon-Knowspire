# KnowSpire

[![Django](https://img.shields.io/badge/Django-5.2-green)](https://www.djangoproject.com/) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Fuel your curiosity. Gamify your growth. Turn mindless scrolling into mindful learning.

---

## 🚀 Overview
KnowSpire is a Django-based web app that transforms curiosity into meaningful, gamified learning. Powered by Google Gemini AI, it delivers personalized lessons, flashcards, and quizzes for any skill you want to learn. Track your progress, earn XP, maintain streaks, and compete on leaderboards.

---

## 🎯 Features
- **Curiosity-Based Learning**: Ask about any topic and get AI-generated lessons, flashcards, and quizzes instantly.
- **Personalized Sessions**: Choose your time slot and learning mode (revision or continue). Gemini AI adapts each session based on what you learned last time.
- **Gamified Progress**:
  - Earn XP for learning, completing sessions, and maintaining daily streaks.
  - Unlock achievements and climb the leaderboard.
- **Streaks**: Daily learning streaks with bonus XP for consistency.
- **Skill Management**:
  - Start, archive, or delete skills.
  - Download your learning data for any skill.
- **Leaderboards**: Compete with friends and see who learns the most.
- **User Profiles**: Track your XP, streaks, and skills in progress.
- **Session Options**: Flexible session durations (10–60 min) and modes (revision/continue).
- **Doubt Mode**: Ask questions during a session and get instant AI-powered answers.
- **Admin Dashboard**: Manage users, skills, and user progress.

---

## 🛠️ Technical Implementation

### Backend
- **Django 5.2**: Robust, scalable, and secure web framework.
- **Models**: UserProfile, Skill, UserSkill track users, skills, progress, XP, streaks, and cached AI content.
- **Services Layer**: Handles Gemini AI integration, XP logic, streaks, and skill completion.
- **Gemini AI Integration**: Uses Google Gemini API for lesson, flashcard, and quiz generation. Prompts are dynamically constructed based on user history and session mode.
- **Session Management**: Each skill session is tracked, with options for revision or continuation. Previous content is cached for context-aware AI responses.
- **XP & Streaks**: Custom logic awards XP for daily activity, session completion, and streak milestones. Streaks are tracked and reset if days are missed.
- **Admin Tools**: Django admin for managing users, skills, and progress.

### Frontend
- **Bootstrap 5**: Responsive, modern UI with custom theming and dark mode support.
- **Templates**: Modular Django templates for dashboard, skills, leaderboard, and session views.
- **Dynamic UI**: JavaScript for theme toggling, modals, and interactive session controls.
- **Progress Visualization**: Weekly progress bars, XP counters, and streak indicators.
- **Gamification Elements**: Badges, leaderboards, and achievement highlights.

### AI & Data
- **Google Gemini API**: Generates lessons, flashcards, quizzes, and answers to doubts in real time.
- **Context-Aware Prompts**: AI sees what was taught last time and chooses the best next topic for the allotted time slot.
- **Caching**: Lessons, flashcards, and quizzes are cached per user/skill for fast retrieval and continuity.

### Security & DevOps
- **Environment Variables**: Sensitive keys (Gemini API) stored in `.env` and ignored by git.
- **User Authentication**: Django's built-in auth system for secure login/register/logout.
- **Email Integration**: SMTP setup for notifications and password resets.
- **Database**: SQLite for quick prototyping; easily swappable for Postgres/MySQL.

---

## 💡 Possibilities
- Learn anything: science, history, coding, languages, and more.
- Use as a personal tutor, revision tool, or curiosity engine.
- Gamify learning for individuals, classrooms, or teams.
- Export and share your learning journey.

---

## 🌱 Future Potential
- **Mobile App**: Native iOS/Android experience.
- **Social Features**: Friend lists, challenges, and collaborative learning.
- **Advanced Analytics**: Deep insights into learning habits and strengths.
- **Custom Content**: User-generated lessons and quizzes.
- **Integrations**: Connect with other learning platforms and productivity tools.
- **Voice & Chatbot Support**: Learn via voice or chat interfaces.
- **Expanded AI Models**: Support for more advanced and specialized AI tutors.
- **Rewards & Badges**: Unlockable achievements and tangible rewards.

---

## ⚙️ Tech Stack
- Django (Python)
- Bootstrap (Frontend)
- Google Gemini AI (Content Generation)
- SQLite (Default DB)

---

## 🚦 Getting Started

```bash
# 1. Clone the repo
$ git clone https://github.com/Shaurya200911/FusionHackathon-Knowspire.git
$ cd knowspire

# 2. (Optional) Create and activate a virtual environment
$ python -m venv venv
$ venv\Scripts\activate  # On Windows

# 3. Install dependencies
$ pip install -r requirements.txt

# 4. Set up your .env file in knowspire/knowspire/
GEMINI_API_KEY=your-gemini-api-key

# 5. Run migrations
$ python manage.py migrate

# 6. Start the server
$ python manage.py runserver
```

Then, register, log in, and start learning!

---

## 🤝 Contributing
Open to feature requests, bug reports, and collaboration. See [issues](https://github.com/yourusername/knowspire/issues) or contact the team.

## 📄 License
MIT

---
KnowSpire: Scroll smarter, not longer. 🚀
