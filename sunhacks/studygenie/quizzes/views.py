from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Quiz, Question, QuizAttempt
from documents.models import Document
import json

def generate_quiz_questions(text, difficulty='medium'):
    """Generate quiz questions from document text using AI with difficulty level"""
    from ai_services import generate_quiz_with_ai
    
    # Ensure we have meaningful content
    if not text or len(text.strip()) < 50:
        fallback_questions = {
            'easy': [{
                "stem": "What type of document is this?",
                "options": {"A": "Study material", "B": "Novel", "C": "Recipe", "D": "Manual"},
                "answer_key": "A",
                "explanation": "This is educational study material."
            }],
            'medium': [{
                "stem": "What's the best approach when content is limited?",
                "options": {"A": "Skip studying", "B": "Find additional resources", "C": "Focus on available content", "D": "Both B and C"},
                "answer_key": "D",
                "explanation": "Finding additional resources while focusing on available material is best."
            }],
            'hard': [{
                "stem": "How would you analyze and improve content extraction from this document?",
                "options": {"A": "Check file format compatibility", "B": "Verify OCR accuracy", "C": "Assess document structure", "D": "All of the above"},
                "answer_key": "D",
                "explanation": "Comprehensive analysis requires checking format, OCR accuracy, and document structure."
            }]
        }
        return fallback_questions.get(difficulty, fallback_questions['medium'])
    
    return generate_quiz_with_ai(text, difficulty)

@login_required
def quiz_view(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, user=request.user)
    
    # Get difficulty from request or default to medium
    difficulty = request.GET.get('difficulty', 'medium')
    
    # Get or create quiz for this document with specific difficulty
    quiz, created = Quiz.objects.get_or_create(
        document=doc,
        difficulty=difficulty,
        defaults={'title': f'{difficulty.title()} Quiz for {doc.title}'}
    )
    
    if created or not quiz.question_set.exists():
        # Generate questions using AI based on document content
        if doc.extracted_text and len(doc.extracted_text.strip()) > 50:
            try:
                questions_data = generate_quiz_questions(doc.extracted_text, difficulty)
                
                for q_data in questions_data:
                    Question.objects.create(
                        quiz=quiz,
                        stem=q_data['stem'],
                        options=q_data['options'],
                        answer_key=q_data['answer_key'],
                        explanation=q_data['explanation']
                    )
            except Exception as e:
                pass
                # Create document-specific fallback questions
                doc_title = doc.title.lower()
                Question.objects.create(
                    quiz=quiz,
                    stem=f"What is the main subject of '{doc.title}'?",
                    options={"A": "Technical concepts", "B": "General information", "C": "Specific topic content", "D": "Mixed content"},
                    answer_key="C",
                    explanation=f"The document '{doc.title}' focuses on specific topic content."
                )
        else:
            # No content available
            Question.objects.create(
                quiz=quiz,
                stem="This document appears to have limited readable content. What should you do?",
                options={"A": "Try a different file", "B": "Check file format", "C": "Ensure file isn't corrupted", "D": "All of the above"},
                answer_key="D",
                explanation="When content extraction fails, checking the file format and integrity is recommended."
            )
    
    questions = quiz.question_set.all()
    return render(request, 'quizzes/quiz.html', {'quiz': quiz, 'questions': questions, 'doc': doc})

@login_required
def submit_quiz(request, quiz_id):
    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.question_set.all()
        
        score = 0
        total = len(questions)
        results = []
        
        for i, question in enumerate(questions):
            user_answer = request.POST.get(f'q{i+1}')
            is_correct = user_answer == question.answer_key
            if is_correct:
                score += 1
            
            results.append({
                'question': question.stem,
                'user_answer': user_answer,
                'correct_answer': question.answer_key,
                'is_correct': is_correct,
                'explanation': question.explanation
            })
        
        # Save attempt
        QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total_questions=total
        )
        
        return render(request, 'quizzes/results.html', {
            'quiz': quiz,
            'score': score,
            'total': total,
            'percentage': round((score/total)*100, 1),
            'results': results
        })
    
    return redirect('quiz', doc_id=quiz.document.id)


