<<<<<<< HEAD
📚 StudyGenie – AI-Powered Study Platform

AI-driven educational web platform that transforms documents into interactive study materials.
Built during SunHacks 2024, it leverages advanced AI for personalized learning experiences with smart summaries, quizzes, flashcards, and real-time assistance.

✨ Features

📄 Document Processing – Upload PDFs & images with OCR (English, Hindi, Marathi, etc.)

🤖 AI Content Generation – Summaries, quizzes, flashcards, keyword extraction

🌍 Multilingual Support – English, Hindi, Marathi, Spanish, French, German

💬 AI Assistant – Chat-based guidance with speech-to-text & text-to-speech

📊 Progress Analytics – Learning streaks, performance tracking, achievements

🎥 YouTube Integration – Auto-recommended educational videos

🏗️ Tech Stack

Backend: Django 4.2.7, Python 3.13+, SQLite
AI/ML: Google Gemini (gemini-1.5-flash), PyPDF2, Pytesseract, Pillow
Frontend: HTML5, CSS3, Bootstrap 5, JavaScript (ES6+), Font Awesome
Other Tools: python-dotenv, Batch Scripts for setup

🚀 Quick Start (Local Setup)
1️⃣ Clone the Repository
git clone https://github.com/your-username/studygenie.git
cd studygenie

2️⃣ Setup Environment
python -m venv venv
venv\Scripts\activate   # On Windows
pip install -r requirements.txt

3️⃣ Run the App Locally
python manage.py migrate
python manage.py runserver


App will be available at 👉 http://127.0.0.1:8000/

📂 Project Structure
studygenie/
├── authentication/    # User login/signup
├── dashboard/         # Main UI
├── documents/         # File upload & processing
├── quizzes/           # Quiz generation
├── flashcards/        # Flashcard system
└── studygenie/        # Core Django settings

🧪 Testing
python manage.py test

🌟 Highlights

Adaptive quiz difficulty (Bloom’s taxonomy)

Multilingual content generation & translation

AI-powered summaries & keyword extraction

Spaced repetition flashcards

Gamified learning with achievements

📋 Roadmap (Future Enhancements)

📱 Mobile app (iOS & Android)

👥 Collaborative group study features

📈 Advanced analytics (ML-driven insights)

☁️ Cloud deployment (future production)

🤝 Contributing

Pull requests are welcome! For major changes, open an issue first to discuss improvements.

🏆 Credits

Built with ❤ by Team SunHacks 2024
Transforming education through AI-powered personalized learning
=======
# SunHacks
StudyGenie – AI-Powered Study Platform -- Hackathon Project
>>>>>>> 585da3a5733b2eaf7d0e4483fa814c7f03edcfeb
