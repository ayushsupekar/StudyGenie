@echo off
echo Setting up StudyGenie...
echo.

echo 1. Installing dependencies...
pip install -r requirements.txt

echo.
echo 2. Running migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo 3. Creating demo users...
python create_users.py

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Add your OpenAI API key to .env file
echo 2. Run: run_server.bat
echo 3. Visit: http://127.0.0.1:8000
echo.
pause


