from django.contrib import admin
from .models import Flashcard, FlashcardReview

@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ['front', 'document', 'created_at']

@admin.register(FlashcardReview)
class FlashcardReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'flashcard', 'difficulty', 'reviewed_at']