@echo off
echo Starting StudyGenie Server...
echo.
echo Make sure you have:
echo 1. Set your OpenAI API key in .env file
echo 2. Installed all dependencies: pip install -r requirements.txt
echo.
echo Login credentials:
echo - Username: demo, Password: demo123
echo - Username: student1, Password: password123
echo - Admin: admin, Password: admin123
echo.
echo Server will start at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver