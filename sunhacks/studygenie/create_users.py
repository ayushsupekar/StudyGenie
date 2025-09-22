import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from django.contrib.auth.models import User

# Create demo users
users = [
    {'username': 'student1', 'password': 'password123', 'email': 'student1@example.com'},
    {'username': 'student2', 'password': 'password123', 'email': 'student2@example.com'},
    {'username': 'demo', 'password': 'demo123', 'email': 'demo@example.com'},
]

#cd g:\ha\sunhacks\studygenie
#pip install Django==4.2.7 Pillow PyPDF2==3.0.1 pytesseract google-generativeai python-dotenv
#python manage.py runserver


for user_data in users:
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults={
            'email': user_data['email'],
            'first_name': user_data['username'].title(),
            'last_name': 'User'
        }
    )
    if created:
        user.set_password(user_data['password'])
        user.save()
        print(f"Created user: {user_data['username']}")
    else:
        print(f"User already exists: {user_data['username']}")

print("\nLogin credentials:")
print("Username: student1, Password: password123")
print("Username: student2, Password: password123") 
print("Username: demo, Password: demo123")
print("Username: admin, Password: admin123 (superuser)")