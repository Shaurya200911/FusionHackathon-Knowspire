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

### Prerequisites
- Python 3.10+ installed ([Download Python](https://www.python.org/downloads/))
- Git installed ([Download Git](https://git-scm.com/downloads))

### 1. Clone the Repository
```bash
git clone https://github.com/Shaurya200911/FusionHackathon-Knowspire.git
cd FusionHackathon-Knowspire/knowspire
```

### 2. Create and Activate a Virtual Environment
#### On Windows
```bash
python -m venv venv
venv\Scripts\activate
```
#### On macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
- Copy `.env.example` (if available) to `.env` in `knowspire/knowspire/`.
- Add your Gemini API key:
```
GEMINI_API_KEY=your-gemini-api-key
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Start the Development Server
```bash
python manage.py runserver
```

### 7. Access the App
- Open your browser and go to [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Register, log in, and start learning!

---

## 📸 Screenshots

Below are screenshots of the KnowSpire website:

![Logo](userauth/assets/images/img_header_logo.png)
![Website Screenshot 1](userauth/assets/images/website1.png)
![Website Screenshot 2](userauth/assets/images/website 2.png)
![Website Screenshot 3](userauth/assets/images/website 3.png)
![Website Screenshot 4](userauth/assets/images/website 4.png)
![Website Screenshot 5](userauth/assets/images/website 5.png)
![Website Screenshot 6](userauth/assets/images/website 6.png)
![Website Screenshot 7](userauth/assets/images/website 7.png)
![Website Screenshot 8](userauth/assets/images/website 8.png)
![Website Screenshot 9](userauth/assets/images/website 9.png)
![Website Screenshot 10](userauth/assets/images/website 10.png)
![Website Screenshot 11](userauth/assets/images/website 11.png)
![Website Screenshot 12](userauth/assets/images/website 12.png)
![Website Screenshot 13](userauth/assets/images/website 13.png)
![Website Screenshot 14](userauth/assets/images/website 14.png)
![Website Screenshot 15](userauth/assets/images/website 15.png)

---

## 🤝 Contributing
Open to feature requests, bug reports, and collaboration. See [issues](https://github.com/yourusername/knowspire/issues) or contact the team.

## 📄 License
MIT

---
KnowSpire: Scroll smarter, not longer. 🚀
