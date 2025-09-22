@echo off
echo ========================================
echo        StudyGenie AI Study Assistant
echo ========================================
echo.
echo Starting StudyGenie with enhanced AI assistant...
echo.
echo Features:
echo - Real-time AI chatbot with Google Gemini
echo - Smart fallback responses when quota exceeded
echo - Voice recognition and text-to-speech
echo - Document analysis and quiz generation
echo.
echo Login credentials:
echo - Username: demo, Password: demo123
echo - Username: student1, Password: password123
echo - Admin: admin, Password: admin123
echo.
echo Server will start at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install requirements if needed
echo Checking dependencies...
pip install -r requirements.txt --quiet

REM Run the server
echo Starting Django server...
python manage.py runserver