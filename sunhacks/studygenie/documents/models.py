from django.db import models
from django.contrib.auth.models import User
import json

class Document(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('mr', 'Marathi'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('auto', 'Auto-detect'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    extracted_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    summary_translations = models.JSONField(default=dict, blank=True)  # Store translations
    youtube_videos = models.TextField(blank=True)  # Store as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='auto')
    detected_language = models.CharField(max_length=5, default='en')
    status = models.CharField(max_length=20, default='uploaded')

    def __str__(self):
        return self.title
    
    def get_youtube_videos(self):
        """Get YouTube videos as Python list"""
        if self.youtube_videos:
            try:
                return json.loads(self.youtube_videos)
            except:
                return []
        return []
    
    def set_youtube_videos(self, videos):
        """Set YouTube videos from Python list"""
        self.youtube_videos = json.dumps(videos)
    
    def get_summary_in_language(self, lang_code):
        """Get summary in specific language"""
        if lang_code == self.detected_language:
            return self.summary
        return self.summary_translations.get(lang_code, self.summary)
    
    def set_summary_translation(self, lang_code, translation):
        """Set summary translation for specific language"""
        if not self.summary_translations:
            self.summary_translations = {}
        self.summary_translations[lang_code] = translation
        self.save()