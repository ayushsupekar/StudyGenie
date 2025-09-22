from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Flashcard, FlashcardReview
from documents.models import Document

def generate_flashcards(text):
    from ai_services import generate_flashcards_with_ai
    return generate_flashcards_with_ai(text)

@login_required
def flashcards_view(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, user=request.user)
    
    # Get or create flashcards for this document
    flashcards = Flashcard.objects.filter(document=doc)
    
    if not flashcards.exists():
        # Generate flashcards using AI
        try:
            cards_data = generate_flashcards(doc.extracted_text)
            
            for card_data in cards_data:
                Flashcard.objects.create(
                    document=doc,
                    front=card_data['front'],
                    back=card_data['back']
                )
        except Exception as e:
            pass
            # Create fallback flashcards
            Flashcard.objects.create(
                document=doc,
                front="What is this document about?",
                back=f"This document '{doc.title}' contains study material."
            )
        
        flashcards = Flashcard.objects.filter(document=doc)
    
    return render(request, 'flashcards/review.html', {'flashcards': flashcards, 'doc': doc})

@login_required
def mark_difficulty(request, flashcard_id):
    if request.method == 'POST':
        flashcard = get_object_or_404(Flashcard, id=flashcard_id)
        difficulty = request.POST.get('difficulty')
        
        FlashcardReview.objects.create(
            user=request.user,
            flashcard=flashcard,
            difficulty=difficulty
        )
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'})