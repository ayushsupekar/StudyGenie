from django.db import models
from documents.models import Document
from django.contrib.auth.models import User

class Flashcard(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('mr', 'Marathi'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    front = models.TextField()
    back = models.TextField()
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    translations = models.JSONField(default=dict, blank=True)  # Store flashcard translations
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.front[:50]
    
    def get_translation(self, lang_code):
        """Get flashcard translation for specific language"""
        if lang_code == self.language:
            return {'front': self.front, 'back': self.back}
        return self.translations.get(lang_code, {'front': self.front, 'back': self.back})
    
    def set_translation(self, lang_code, front_text, back_text):
        """Set flashcard translation for specific language"""
        if not self.translations:
            self.translations = {}
        self.translations[lang_code] = {'front': front_text, 'back': back_text}
        self.save()

class FlashcardReview(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    reviewed_at = models.DateTimeField(auto_now_add=True)