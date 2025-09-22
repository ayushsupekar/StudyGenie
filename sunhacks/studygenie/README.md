# StudyGenie - AI-Powered Study Companion 🧞‍♂️

## 🚀 Features
- **Smart Document Upload** - PDFs and images with OCR
- **AI-Generated Summaries** - Powered by OpenAI GPT
- **Dynamic Quizzes** - Contextual MCQs with explanations
- **Interactive Flashcards** - Spaced repetition system
- **AI Tutor Chat** - Ask questions about your materials
- **Progress Analytics** - Track learning streaks and scores
- **Multi-language Support** - Summaries in multiple languages

## ⚡ Quick Setup

### Option 1: Automated Setup (Windows)
```bash
# Run the setup script
setup.bat

# Add your OpenAI API key to .env
# Then start the server
run_server.bat
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up OpenAI API
copy .env.example .env
# Edit .env: OPENAI_API_KEY=sk-your-actual-api-key-here

# 3. Setup database
python manage.py makemigrations
python manage.py migrate
python create_users.py

# 4. Start server
python manage.py runserver
```

## 🔑 Login Credentials
- **Demo User**: `demo` / `demo123`
- **Student**: `student1` / `password123`
- **Admin**: `admin` / `admin123`

## 📖 Usage Guide

1. **Login** → Use any of the demo credentials
2. **Upload** → Select PDF/image file (study notes, textbooks, etc.)
3. **Study** → View AI-generated summary of your material
4. **Practice** → Take personalized quizzes based on content
5. **Review** → Use flashcards with spaced repetition
6. **Ask** → Chat with AI tutor about specific questions
7. **Track** → Monitor progress and learning streaks

## 🛠 Tech Stack
- **Backend**: Django 4.2, SQLite
- **Frontend**: Bootstrap 5, JavaScript
- **AI**: OpenAI GPT-3.5-turbo
- **Processing**: PyPDF2, Pytesseract OCR
- **Deployment**: Python 3.13+

## 🌟 Key Workflows

### Document Processing Pipeline
```
Upload → Text Extraction → AI Processing → Content Generation
   ↓           ↓              ↓              ↓
 PDF/IMG → OCR/Parse → OpenAI API → Summary/Quiz/Cards
```

### AI-Powered Features
- **Summaries**: Contextual, length-adjustable content overviews
- **Quizzes**: Auto-generated MCQs with explanations
- **Flashcards**: Key terms and definitions extraction
- **Tutor**: RAG-based Q&A using document context

## 🔧 Configuration

### OpenAI API Setup
1. Get API key: https://platform.openai.com/api-keys
2. Add to `.env`: `OPENAI_API_KEY=sk-your-key`
3. Restart server

### Admin Panel
- URL: http://127.0.0.1:8000/admin/
- Manage users, documents, quizzes, progress

## 🎯 Perfect for
- **Students** - Convert textbooks into study materials
- **Educators** - Create quizzes from course content
- **Professionals** - Learn from technical documents
- **Researchers** - Summarize academic papers