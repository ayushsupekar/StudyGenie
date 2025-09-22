# 🌍 Multilanguage Feature Documentation

## Overview
The StudyGenie platform now supports multilanguage functionality, allowing users to generate and view study materials (summaries, quizzes, and flashcards) in multiple languages.

## Supported Languages
- 🇺🇸 **English** (en)
- 🇮🇳 **Hindi** (hi) - हिंदी
- 🇮🇳 **Marathi** (mr) - मराठी  
- 🇪🇸 **Spanish** (es) - Español
- 🇫🇷 **French** (fr) - Français
- 🇩🇪 **German** (de) - Deutsch

## Features

### 1. Language Detection
- **Auto-detect**: Automatically detects the primary language of uploaded documents
- **Manual selection**: Users can manually specify the preferred language during upload

### 2. Multilingual Content Generation
- **Summaries**: Generate AI summaries in any supported language
- **Quizzes**: Create quiz questions with options and explanations in target language
- **Flashcards**: Generate flashcards with front/back content in specified language

### 3. Real-time Translation
- **On-demand translation**: Translate existing content to different languages
- **Cached translations**: Store translations to avoid regenerating the same content
- **Language switching**: Switch between languages in the summary view

## How to Use

### During Upload
1. Select your preferred language from the dropdown
2. Optionally check additional languages for multilingual generation
3. Upload your document
4. The system will generate content in your selected language(s)

### After Upload
1. **Language Switching**: Use the language dropdown in the summary view
2. **Translate Summary**: Click the "Translate" button to translate to current language
3. **Generate Quiz**: Click "Quiz in Language" to create questions in current language
4. **Generate Flashcards**: Click "Generate in Current Language" for flashcards

## API Endpoints

### Translation Endpoints
- `POST /documents/<id>/translate/` - Translate summary to target language
- `POST /documents/<id>/quiz-lang/` - Generate quiz in specific language  
- `POST /documents/<id>/flashcards-lang/` - Generate flashcards in specific language
- `POST /documents/<id>/multilang/` - Generate content in multiple languages

### Request Format
```json
{
    "language": "hi",
    "type": "summary",
    "difficulty": "medium"
}
```

### Response Format
```json
{
    "success": true,
    "content": "Generated content...",
    "language": "hi",
    "cached": false
}
```

## Database Schema

### Document Model
```python
class Document(models.Model):
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='auto')
    detected_language = models.CharField(max_length=5, default='en')
    summary_translations = models.JSONField(default=dict, blank=True)
```

### Quiz Model
```python
class Quiz(models.Model):
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')

class Question(models.Model):
    translations = models.JSONField(default=dict, blank=True)
```

### Flashcard Model
```python
class Flashcard(models.Model):
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    translations = models.JSONField(default=dict, blank=True)
```

## AI Services

### Core Functions
- `detect_language(text)` - Detect primary language of text
- `generate_summary_with_language(text, language)` - Generate summary in specific language
- `generate_quiz_with_language(text, language, difficulty)` - Generate quiz in specific language
- `generate_flashcards_with_language(text, language)` - Generate flashcards in specific language
- `translate_content(text, target_language)` - Translate content to target language
- `generate_multilingual_content(document, target_languages)` - Generate content in multiple languages

### Language-Specific Prompts
The system uses language-specific prompts to ensure culturally appropriate and linguistically accurate content generation.

## User Interface

### Upload Form
- Language selection dropdown
- Multilanguage checkboxes for additional languages
- Visual indicators for supported languages

### Summary View
- Language switcher dropdown
- Real-time translation buttons
- Language-specific content generation buttons
- Current language indicator

### Interactive Features
- **Language Switching**: Seamless switching between languages
- **Loading Indicators**: Visual feedback during translation/generation
- **Error Handling**: Graceful fallback for translation failures
- **Caching**: Efficient storage and retrieval of translations

## Technical Implementation

### Frontend (JavaScript)
```javascript
function switchLanguage(langCode) {
    // Show loading indicator
    // Redirect with language parameter
    window.location.href = `?lang=${langCode}`;
}

function translateSummary() {
    // AJAX call to translation endpoint
    // Update UI with translated content
}
```

### Backend (Django Views)
```python
def summary_view(request, doc_id):
    requested_lang = request.GET.get('lang', doc.detected_language or 'en')
    summary = doc.get_summary_in_language(requested_lang)
    # Return context with language-specific content
```

## Performance Optimizations

1. **Translation Caching**: Store translations in database to avoid regeneration
2. **Lazy Loading**: Generate translations only when requested
3. **Efficient Queries**: Minimize database calls for language switching
4. **Fallback Handling**: Graceful degradation when AI services are unavailable

## Testing

Run the multilanguage test suite:
```bash
python test_multilang.py
```

This will test:
- Language detection accuracy
- Multilingual content generation
- Translation functionality
- Error handling

## Future Enhancements

1. **More Languages**: Add support for additional languages
2. **Voice Support**: Text-to-speech in multiple languages
3. **Cultural Adaptation**: Region-specific content adaptation
4. **Collaborative Translation**: User-contributed translations
5. **Language Learning**: Integration with language learning features

## Troubleshooting

### Common Issues
1. **Translation Fails**: Check AI service availability and API keys
2. **Language Not Detected**: Ensure sufficient text content for detection
3. **UI Not Updating**: Check JavaScript console for errors
4. **Database Errors**: Ensure migrations are applied

### Debug Mode
Enable debug logging in `ai_services.py` to troubleshoot AI-related issues.

## Conclusion

The multilanguage feature makes StudyGenie accessible to a global audience, enabling users to learn in their preferred language while maintaining the quality and accuracy of AI-generated content.

---
*Last updated: December 2024*
*Version: 1.0.0*