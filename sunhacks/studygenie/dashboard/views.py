from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from documents.models import Document
from quizzes.models import QuizAttempt
from flashcards.models import FlashcardReview
from django.db.models import Avg, Count
from django.contrib import messages

@login_required
def dashboard_view(request):
    user = request.user
    
    # Get user's documents
    documents = Document.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Calculate progress stats
    quiz_attempts = QuizAttempt.objects.filter(user=user)
    total_quizzes = quiz_attempts.count()
    avg_score = quiz_attempts.aggregate(Avg('score'))['score__avg'] or 0
    
    # Calculate streak (simplified)
    recent_attempts = quiz_attempts.order_by('-completed_at')[:5]
    streak = 0
    for attempt in recent_attempts:
        if (attempt.score / attempt.total_questions) >= 0.7:
            streak += 1
        else:
            break
    
    # Flashcard reviews
    flashcard_reviews = FlashcardReview.objects.filter(user=user).count()
    
    context = {
        'documents': documents,
        'total_documents': Document.objects.filter(user=user).count(),
        'total_quizzes': total_quizzes,
        'avg_score': round(avg_score, 1),
        'streak': streak,
        'flashcard_reviews': flashcard_reviews,

    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'dashboard/profile.html')