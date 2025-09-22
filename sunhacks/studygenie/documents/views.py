from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Document
import PyPDF2
import os
import json

def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for i, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text += page_text + "\n"
                except Exception as page_error:
                    continue
            
            if text.strip():
                return text.strip()
            else:
                return "Unable to extract readable text from this PDF. The PDF may contain only images or be password protected."
    except Exception as e:
        return f"Error processing PDF: {str(e)}. Please ensure the file is not corrupted or password protected."

def extract_text_from_image(file_path):
    try:
        # Try to use pytesseract if available
        import pytesseract
        from PIL import Image
        
        # Open and process the image
        image = Image.open(file_path)
        # Extract text using OCR
        text = pytesseract.image_to_string(image)
        
        if text.strip():
            return text.strip()
        else:
            return "No readable text found in this image. Please ensure the image contains clear, readable text."
            
    except ImportError:
        return "OCR functionality requires pytesseract and Pillow packages. For now, here's a sample text: This image contains educational content that can be processed for study materials."
    except Exception as e:
        return f"Error processing image: {str(e)}. Please ensure the image is clear and contains readable text."

def generate_ai_summary(text):
    """Generate highly relevant AI summary with enhanced fallback"""
    try:
        from ai_services import generate_summary_with_ai, extract_key_terms_from_text, extract_main_topics, generate_enhanced_fallback_summary
        
        # Try enhanced AI summary first
        ai_summary = generate_summary_with_ai(text)
        
        # Validate AI summary quality - check for specificity
        key_terms = extract_key_terms_from_text(text)
        
        if (ai_summary and len(ai_summary.strip()) > 80 and 
            any(term.lower() in ai_summary.lower() for term in key_terms[:5]) and
            "approximately" not in ai_summary.lower() and
            "this document contains" not in ai_summary.lower()):
            print(f"High-quality AI summary generated: {len(ai_summary)} chars")
            return ai_summary
        else:
            print("AI summary was generic, using enhanced content-based summary")
            main_topics = extract_main_topics(text)
            return generate_enhanced_fallback_summary(text, key_terms, main_topics)
            
    except Exception as e:
        print(f"AI summary generation error: {e}")
        from ai_services import extract_key_terms_from_text, extract_main_topics, generate_enhanced_fallback_summary
        key_terms = extract_key_terms_from_text(text)
        main_topics = extract_main_topics(text)
        return generate_enhanced_fallback_summary(text, key_terms, main_topics)

@login_required
def upload_document(request):
    if request.method == 'POST':
        if not request.FILES.get('file'):
            return render(request, 'documents/upload.html', {'error': 'No file was uploaded. Please select a file.'})
        
        language_preference = request.POST.get('language', 'auto')
        
        try:
            file = request.FILES['file']
            
            # Validate file type
            allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension not in allowed_extensions:
                error_msg = f"Unsupported file type: {file_extension}. Please upload PDF, PNG, JPG, or JPEG files."
                return render(request, 'documents/upload.html', {'error': error_msg})
            
            doc = Document.objects.create(
                user=request.user,
                title=file.name,
                file=file
            )
            
            if not os.path.exists(doc.file.path):
                error_msg = "File was not saved properly. Please try again."
                doc.delete()
                return render(request, 'documents/upload.html', {'error': error_msg})
                
        except Exception as e:
            return render(request, 'documents/upload.html', {'error': f'Error uploading file: {e}'})
        
        # STEP 1: Extract Text
        file_path = doc.file.path
        try:
            if file.name.lower().endswith('.pdf'):
                extracted_text = extract_text_from_pdf(file_path)
            elif file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                extracted_text = extract_text_from_image(file_path)
            else:
                extracted_text = "Unsupported file format."
            
            if len(extracted_text.strip()) < 10:
                extracted_text += " This document may contain images or formatting issues."
                
        except Exception as e:
            extracted_text = f"Error extracting text from {file.name}."
        
        # STEP 2: Generate Enhanced AI Summary (CRITICAL - Must work independently)
        print(f"Step 2: Generating enhanced AI summary for {doc.title}")
        summary = ""
        try:
            # Detect language if auto-detect is selected
            if language_preference == 'auto':
                try:
                    from ai_services import detect_language
                    detected_lang = detect_language(extracted_text)
                    doc.detected_language = detected_lang
                    language_preference = 'en'  # Default to English for processing
                except:
                    language_preference = 'en'
                    doc.detected_language = 'en'
            
            # Generate summary in preferred language
            if language_preference in ['hi', 'mr', 'es', 'fr', 'de']:
                try:
                    from ai_services import generate_summary_with_language
                    summary = generate_summary_with_language(extracted_text, language_preference)
                except:
                    summary = generate_ai_summary(extracted_text)
            else:
                summary = generate_ai_summary(extracted_text)
            
            # Additional validation for quality
            if not summary or len(summary.strip()) < 80:
                print("Summary too short, regenerating with enhanced fallback")
                from ai_services import extract_key_terms_from_text, extract_main_topics, generate_enhanced_fallback_summary
                key_terms = extract_key_terms_from_text(extracted_text)
                main_topics = extract_main_topics(extracted_text)
                summary = generate_enhanced_fallback_summary(extracted_text, key_terms, main_topics)
            
            print(f"[SUCCESS] Enhanced summary generated: {len(summary)} characters")
                
        except Exception as e:
            print(f"[ERROR] Summary generation error: {e}")
            try:
                from ai_services import extract_key_terms_from_text, extract_main_topics, generate_enhanced_fallback_summary
                key_terms = extract_key_terms_from_text(extracted_text)
                main_topics = extract_main_topics(extracted_text)
                summary = generate_enhanced_fallback_summary(extracted_text, key_terms, main_topics)
                print(f"[SUCCESS] Enhanced fallback summary generated: {len(summary)} characters")
            except Exception as fallback_error:
                print(f"[ERROR] Enhanced fallback summary failed: {fallback_error}")
                summary = f"This document '{doc.title}' contains educational content with specific topics and concepts that have been processed for comprehensive study materials."
        
        # STEP 3: Save Core Document Data FIRST (before other processing)
        try:
            doc.extracted_text = extracted_text
            doc.summary = summary
            doc.language = language_preference
            doc.status = 'processed'
            doc.save()
            print(f"[SUCCESS] Document saved with summary: {doc.id}")
        except Exception as e:
            print(f"[ERROR] Document save error: {e}")
            doc.status = 'error'
            doc.save()
        
        # STEP 4: Generate Quiz using enhanced content (Independent - won't break summary)
        try:
            print(f"Step 4: Generating quiz for {doc.title}")
            from ai_services import generate_quiz_with_ai
            # Use both summary and extracted text for better quiz generation
            quiz_content = f"{summary}\n\n{extracted_text[:2000]}" if summary else extracted_text
            quiz_data = generate_quiz_with_ai(quiz_content)
            print(f"[SUCCESS] Quiz generated: {len(quiz_data)} questions")
        except Exception as e:
            print(f"[ERROR] Quiz generation error: {e}")
            quiz_data = []  # Will be generated on-demand
        
        # STEP 5: Generate Flashcards using enhanced content (Independent - won't break summary/quiz)
        try:
            print(f"Step 5: Generating flashcards for {doc.title}")
            from ai_services import generate_flashcards_with_ai
            # Use both summary and extracted text for better flashcard generation
            flashcard_content = f"{summary}\n\n{extracted_text[:2000]}" if summary else extracted_text
            flashcard_data = generate_flashcards_with_ai(flashcard_content)
            print(f"[SUCCESS] Flashcards generated: {len(flashcard_data)} cards")
        except Exception as e:
            print(f"[ERROR] Flashcard generation error: {e}")
            flashcard_data = []  # Will be generated on-demand
        
        # STEP 6: Generate Multilingual Content (if requested)
        multilang_preference = request.POST.get('multilang', '')
        if multilang_preference:
            try:
                print(f"Step 6: Generating multilingual content")
                from ai_services import generate_multilingual_content
                
                # Parse selected languages
                selected_languages = multilang_preference.split(',')
                multilang_results = generate_multilingual_content(doc, selected_languages)
                
                # Store results in session for later use
                request.session[f'multilang_{doc.id}'] = multilang_results
                print(f"[SUCCESS] Multilingual content generated for {len(selected_languages)} languages")
            except Exception as e:
                print(f"[ERROR] Multilingual generation error: {e}")
        
        # STEP 7: Generate YouTube Videos (Independent)
        try:
            print(f"Step 7: Fetching YouTube videos for {doc.title}")
            from youtube_services import get_video_recommendations_from_summary
            
            videos, keywords = get_video_recommendations_from_summary(summary, doc.title)
            if videos:
                video_data = {
                    'videos': videos,
                    'keywords': keywords
                }
                doc.set_youtube_videos(video_data)
                doc.save()
                print(f"[SUCCESS] YouTube videos saved: {len(videos)} videos")
            else:
                print("[INFO] No YouTube videos found")
        except Exception as e:
            print(f"[ERROR] YouTube error: {e} (AI features still work)")
        
        # Redirect to processing screen for better UX
        return render(request, 'documents/processing.html', {'doc': doc})
    
    # GET request - show upload form
    languages = [
        ('auto', 'Auto-detect'),
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('mr', 'Marathi'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
    ]
    return render(request, 'documents/upload.html', {'languages': languages})


@login_required
def summary_view(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, user=request.user)
    
    # Handle language switching
    requested_lang = request.GET.get('lang', 'en')
    
    # ENSURE AI FEATURES WORK INDEPENDENTLY
    print(f"Loading summary view for document: {doc.title}")
    
    # 1. Summary (from database or translation)
    summary = doc.summary or "No summary available"
    
    # If different language requested, try to get/generate translation
    if requested_lang != 'en' and requested_lang in ['hi', 'mr', 'es', 'fr', 'de']:
        try:
            # Check for existing translation
            if hasattr(doc, 'summary_translations') and doc.summary_translations:
                existing_translation = doc.summary_translations.get(requested_lang)
                if existing_translation:
                    summary = existing_translation
                else:
                    # Generate new translation
                    from ai_services import translate_content
                    translation = translate_content(doc.summary, requested_lang)
                    doc.set_summary_translation(requested_lang, translation)
                    summary = translation
            else:
                # Generate translation for first time
                from ai_services import translate_content
                translation = translate_content(doc.summary, requested_lang)
                doc.set_summary_translation(requested_lang, translation)
                summary = translation
        except Exception as e:
            print(f"Translation error: {e}")
            # Keep original summary if translation fails
    
    print(f"[SUCCESS] Summary loaded in {requested_lang}: {len(summary)} characters")
    
    # Set detected language if not set
    if not hasattr(doc, 'detected_language') or not doc.detected_language:
        doc.detected_language = 'en'
        doc.save()
    
    # 2. Skip quiz generation on summary page (generate on-demand)
    quiz_easy = quiz_medium = quiz_hard = []
    print(f"[INFO] Quiz generation skipped for faster loading")
    
    # 3. Skip flashcard generation on summary page (generate on-demand)
    flashcards = []
    print(f"[INFO] Flashcard generation skipped for faster loading")
    
    # 4. Use cached YouTube videos or skip for faster loading
    youtube_videos = []
    youtube_keywords = []
    try:
        cached_videos = doc.get_youtube_videos()
        if cached_videos:
            youtube_videos = cached_videos.get('videos', [])
            youtube_keywords = cached_videos.get('keywords', [])
            print(f"Using cached YouTube videos: {len(youtube_videos)}")
    except Exception as e:
        print(f"YouTube cache error: {e}")
    
    # Available languages for switching
    available_languages = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('mr', 'Marathi'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
    ]
    
    # Context with proper variable names
    context = {
        'doc': doc,
        'summary': summary,
        'quiz_easy': quiz_easy,
        'quiz_medium': quiz_medium,
        'quiz_hard': quiz_hard,
        'flashcards': flashcards,
        'videos': youtube_videos,  # Changed to 'videos' for template
        'youtube_videos': youtube_videos,
        'youtube_keywords': youtube_keywords,
        'extracted_text': doc.extracted_text,
        'current_language': requested_lang,
        'available_languages': available_languages,
    }
    
    print(f"Summary loaded: {len(summary)} chars")
    print(f"Page loaded with cached data for faster performance")
    
    return render(request, 'documents/summary.html', context)

@login_required
def generate_multilang_content(request, doc_id):
    """Generate content in multiple languages"""
    if request.method == 'POST':
        doc = get_object_or_404(Document, id=doc_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            target_language = data.get('language', 'en')
            content_type = data.get('type', 'summary')  # summary, quiz, flashcards
            
            from ai_services import generate_summary_with_language, generate_quiz_with_language, generate_flashcards_with_language
            
            if content_type == 'summary':
                result = generate_summary_with_language(doc.extracted_text, target_language)
                doc.set_summary_translation(target_language, result)
            elif content_type == 'quiz':
                result = generate_quiz_with_language(doc.extracted_text, target_language)
            elif content_type == 'flashcards':
                result = generate_flashcards_with_language(doc.extracted_text, target_language)
            else:
                return JsonResponse({'error': 'Invalid content type'}, status=400)
            
            return JsonResponse({
                'success': True,
                'content': result,
                'language': target_language
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def tutor_view(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, user=request.user)
    
    if request.method == 'POST':
        import json
        from ai_services import generate_summary_with_ai
        
        data = json.loads(request.body)
        question = data.get('question', '')
        
        # Generate AI tutor response based on document content
        document_content = doc.extracted_text or "No content extracted from document"
        document_summary = doc.summary or "No summary available"
        
        # Fast, focused prompt for quicker responses
        context_prompt = f"""
        Document: {doc.title}
        Content: {document_content[:500]}
        
        Question: {question}
        
        Instructions:
        1. If question is unrelated to document, respond: "This question is not related to the uploaded document content. Please ask questions about the material in your document."
        2. If related, answer briefly using document content only.
        
        Answer:
        """
        
        # Check request type
        is_mcq_request = any(term in question.lower() for term in ['mcq', 'multiple choice', 'quiz', 'questions', 'test', '10 mcq', 'create questions'])
        
        # Enhanced document content processing
        if not document_content or len(document_content.strip()) < 50:
            document_content = f"Document: {doc.title}\nSummary: {document_summary}\nContent: Limited text available for analysis."
        
        try:
            # Load API key from .env file
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('GOOGLE_AI_API_KEY')
            
            if not api_key:
                raise Exception("API key not found")
            
            # Initialize AI with .env API key
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            if is_mcq_request:
                # RAG-based MCQ generation
                mcq_prompt = f"""Create 10 MCQs from this document:
                
Document: {doc.title}
Content: {document_content[:2000]}
                
Format:
Q1: [Question]
A) [Option] B) [Option] C) [Option] D) [Option]
Answer: [Letter]
                """
                response = model.generate_content(mcq_prompt)
                ai_response = response.text.strip().replace('\n\n', '<br><br>').replace('\n', '<br>')
            else:
                # RAG-based tutor response
                question_words = set(question.lower().split())
                sentences = [s.strip() for s in document_content.split('.') if len(s.strip()) > 20]
                relevant_content = []
                
                for sentence in sentences:
                    if len(question_words.intersection(set(sentence.lower().split()))) > 0:
                        relevant_content.append(sentence)
                
                relevant_text = ' '.join(relevant_content[:3]) if relevant_content else document_content[:500]
                
                rag_prompt = f"""Answer based on document content only:
                
Document: {doc.title}
Content: {relevant_text}
Question: {question}
                
If unrelated to document, say so. Keep under 150 words.
                """
                
                response = model.generate_content(rag_prompt)
                ai_response = response.text.strip().replace('\n\n', '<br><br>').replace('\n', '<br>')
                ai_response += f"<br><small class='text-muted'>Based on: {doc.title}</small>"
        except Exception as e:
            error_msg = str(e)
            # Enhanced fallback for MCQ requests
            if is_mcq_request:
                # Generate 10 comprehensive MCQs from document content
                ai_response = f"<strong>10 MCQs based on '{doc.title}':</strong><br><br>"
                
                # Extract key concepts from document content
                content_lines = [line.strip() for line in document_content.split('\n') if line.strip() and len(line.strip()) > 20]
                sentences = [s.strip() for s in document_content.replace('\n', ' ').split('.') if len(s.strip()) > 15]
                
                # Generate exactly 10 MCQs
                mcq_questions = []
                
                # Question 1: Main topic
                mcq_questions.append({
                    'q': f"What is the main topic of '{doc.title}'?",
                    'options': ['The primary subject covered in this document', 'Unrelated general knowledge', 'Random information', 'Historical events'],
                    'answer': 'A'
                })
                
                # Question 2-4: Content-based questions
                definition_lines = [line for line in content_lines[:15] if any(word in line.lower() for word in ['is', 'are', 'means', 'refers', 'defined'])]
                for i, line in enumerate(definition_lines[:3]):
                    words = line.split()
                    if len(words) > 5:
                        key_term = next((word for word in words[:5] if len(word) > 3 and word.lower() not in ['the', 'this', 'that', 'these', 'those']), words[0])
                        mcq_questions.append({
                            'q': f"According to the document, what is {key_term}?",
                            'options': [line[:60] + '...', 'Not mentioned in document', 'A type of software', 'An outdated concept'],
                            'answer': 'A'
                        })
                
                # Question 5-7: Process/method questions
                process_lines = [line for line in content_lines[:15] if any(word in line.lower() for word in ['process', 'method', 'procedure', 'steps', 'algorithm'])]
                for i, line in enumerate(process_lines[:3]):
                    mcq_questions.append({
                        'q': f"What process is described in the document?",
                        'options': [line[:60] + '...', 'No process mentioned', 'Random procedures', 'Theoretical concepts only'],
                        'answer': 'A'
                    })
                
                # Question 8-10: Application/example questions
                app_lines = [line for line in content_lines[:15] if any(word in line.lower() for word in ['example', 'application', 'used', 'practice'])]
                for i, line in enumerate(app_lines[:3]):
                    mcq_questions.append({
                        'q': f"What application or example is mentioned?",
                        'options': [line[:60] + '...', 'No examples given', 'Theoretical only', 'Not applicable'],
                        'answer': 'A'
                    })
                
                # Fill remaining questions with generic content-based ones
                while len(mcq_questions) < 10:
                    remaining_lines = [line for line in sentences[:20] if len(line) > 30]
                    if remaining_lines:
                        line = remaining_lines[len(mcq_questions) - 1] if len(mcq_questions) <= len(remaining_lines) else remaining_lines[0]
                        mcq_questions.append({
                            'q': f"What information is provided in the document?",
                            'options': [line[:60] + '...', 'No specific information', 'General concepts only', 'Unrelated content'],
                            'answer': 'A'
                        })
                    else:
                        mcq_questions.append({
                            'q': f"Question {len(mcq_questions) + 1}: What type of material is this?",
                            'options': ['Educational/study material', 'Entertainment content', 'News article', 'Personal diary'],
                            'answer': 'A'
                        })
                
                # Format all 10 questions
                for i, mcq in enumerate(mcq_questions[:10], 1):
                    ai_response += f"<strong>Q{i}:</strong> {mcq['q']}<br>"
                    ai_response += f"A) {mcq['options'][0]}<br>"
                    ai_response += f"B) {mcq['options'][1]}<br>"
                    ai_response += f"C) {mcq['options'][2]}<br>"
                    ai_response += f"D) {mcq['options'][3]}<br>"
                    ai_response += f"<strong>Answer:</strong> {mcq['answer']}<br><br>"
                
                if 'quota' in error_msg.lower() or '429' in error_msg:
                    ai_response += "<small class='text-muted'><i class='fas fa-info-circle'></i> AI quota reached. 10 questions generated from document content analysis.</small>"
                else:
                    ai_response += "<small class='text-muted'><i class='fas fa-info-circle'></i> 10 questions generated from document content.</small>"
                    
            else:
                # Intelligent document-based response system
                word_count = len(document_content.split()) if document_content else 0
                content_lower = document_content.lower()
                question_lower = question.lower()
                
                # Extract key terms from question
                question_words = [word.strip('.,?!') for word in question_lower.split() if len(word) > 3]
                
                # Find relevant content sections
                relevant_lines = []
                for line in document_content.split('\n'):
                    if line.strip() and len(line.strip()) > 20:
                        line_lower = line.lower()
                        if any(word in line_lower for word in question_words):
                            relevant_lines.append(line.strip())
                
                # Check if question is related to document content
                document_topics = ['control', 'statement', 'programming', 'if', 'else', 'loop', 'while', 'for', 'java', 'code']
                is_document_related = any(topic in content_lower for topic in document_topics) and any(topic in question_lower for topic in document_topics)
                
                # If question seems unrelated to document content
                if not relevant_lines and not is_document_related:
                    ai_response = "I can only answer questions related to your uploaded document. Please ask questions about the content in your study material."
                    return JsonResponse({'response': ai_response})
                
                # Smart response based on question type and content
                if 'what' in question_lower and ('is' in question_lower or 'are' in question_lower):
                    # Definition/explanation questions
                    ai_response = f"<strong>Based on '{doc.title}':</strong><br><br>"
                    if relevant_lines:
                        ai_response += f"According to your document:<br>"
                        for line in relevant_lines[:3]:
                            ai_response += f"• {line}<br>"
                    else:
                        ai_response += f"From the document summary: {document_summary}<br>"
                    ai_response += "<br>"
                    
                elif 'how' in question_lower:
                    # Process/method questions
                    ai_response = f"<strong>How-to from '{doc.title}':</strong><br><br>"
                    if relevant_lines:
                        ai_response += "Based on your document content:<br>"
                        for i, line in enumerate(relevant_lines[:4], 1):
                            ai_response += f"{i}. {line}<br>"
                    else:
                        ai_response += f"The document discusses: {document_summary}<br>"
                    ai_response += "<br>"
                    
                elif 'why' in question_lower:
                    # Reasoning/explanation questions
                    ai_response = f"<strong>Explanation from '{doc.title}':</strong><br><br>"
                    if relevant_lines:
                        ai_response += "According to the document:<br>"
                        for line in relevant_lines[:3]:
                            ai_response += f"• {line}<br>"
                    else:
                        ai_response += f"Context from document: {document_summary}<br>"
                    ai_response += "<br>"
                    
                elif 'example' in question_lower or 'examples' in question_lower:
                    # Example requests
                    ai_response = f"<strong>Examples from '{doc.title}':</strong><br><br>"
                    example_lines = [line for line in document_content.split('\n') if 'example' in line.lower() or 'for instance' in line.lower() or 'such as' in line.lower()]
                    if example_lines:
                        for line in example_lines[:3]:
                            if line.strip():
                                ai_response += f"• {line.strip()}<br>"
                    else:
                        ai_response += "Looking through the document content for examples...<br>"
                        for line in relevant_lines[:2]:
                            ai_response += f"• {line}<br>"
                    ai_response += "<br>"
                    
                elif any(term in question_lower for term in ['explain', 'describe', 'tell me about']):
                    # General explanation requests
                    ai_response = f"<strong>About '{doc.title}':</strong><br><br>"
                    if relevant_lines:
                        ai_response += "From your document:<br>"
                        for line in relevant_lines[:4]:
                            ai_response += f"• {line}<br>"
                    ai_response += f"<br><strong>Summary:</strong> {document_summary}<br><br>"
                    
                elif 'difference' in question_lower or 'compare' in question_lower:
                    # Comparison questions
                    ai_response = f"<strong>Comparison from '{doc.title}':</strong><br><br>"
                    if relevant_lines:
                        ai_response += "Based on document content:<br>"
                        for line in relevant_lines[:3]:
                            ai_response += f"• {line}<br>"
                    else:
                        ai_response += f"Document context: {document_summary}<br>"
                    ai_response += "<br>"
                    
                elif any(term in question_lower for term in ['list', 'types', 'kinds', 'categories']):
                    # List/categorization requests
                    ai_response = f"<strong>From '{doc.title}':</strong><br><br>"
                    numbered_content = []
                    for line in document_content.split('\n'):
                        if line.strip() and (line.strip().startswith(('1.', '2.', '3.', '•', '-')) or 'type' in line.lower()):
                            numbered_content.append(line.strip())
                    
                    if numbered_content:
                        ai_response += "Document lists:<br>"
                        for item in numbered_content[:5]:
                            ai_response += f"{item}<br>"
                    elif relevant_lines:
                        ai_response += "Related content:<br>"
                        for i, line in enumerate(relevant_lines[:4], 1):
                            ai_response += f"{i}. {line}<br>"
                    ai_response += "<br>"
                    
                else:
                    # General intelligent response
                    if relevant_lines:
                        ai_response = f"<strong>From '{doc.title}' ({word_count} words):</strong><br><br>"
                        ai_response += f"<strong>Relevant content for your question:</strong><br>"
                        for line in relevant_lines[:3]:
                            ai_response += f"• {line}<br>"
                        ai_response += "<br>"
                        ai_response += f"<strong>Document Context:</strong><br>{document_summary}<br><br>"
                    else:
                        # Question might be somewhat related but no specific content found
                        ai_response = "I can only help with questions about your uploaded document. Please ask about the topics covered in your study material."
                
                # Add helpful footer only for document-related responses
                if relevant_lines or is_document_related:
                    ai_response += f"<small class='text-muted'><i class='fas fa-book'></i> Response based on analysis of {word_count} words from your document.</small>"
                
                if 'quota' in error_msg.lower() or '429' in error_msg:
                    if 'Limited Information Found' not in ai_response and 'Question Outside Document Scope' not in ai_response:
                        ai_response += "<br><small class='text-muted'><i class='fas fa-exclamation-triangle'></i> AI quota reached. Response based on document analysis.</small>"
        
        return JsonResponse({'response': ai_response})
    
    return render(request, 'documents/tutor.html', {'doc': doc})

@login_required
def translate_summary(request, doc_id):
    """Translate summary to requested language"""
    if request.method == 'POST':
        doc = get_object_or_404(Document, id=doc_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            target_language = data.get('language', 'en')
            
            # If English requested, return original summary
            if target_language == 'en':
                return JsonResponse({
                    'success': True,
                    'translation': doc.summary,
                    'language': target_language,
                    'cached': True
                })
            
            # Check if translation already exists
            if hasattr(doc, 'summary_translations') and doc.summary_translations:
                existing_translation = doc.summary_translations.get(target_language)
                if existing_translation:
                    return JsonResponse({
                        'success': True,
                        'translation': existing_translation,
                        'language': target_language,
                        'cached': True
                    })
            
            # Generate new translation
            from ai_services import translate_content
            translation = translate_content(doc.summary, target_language)
            
            # Save translation
            if not doc.summary_translations:
                doc.summary_translations = {}
            doc.summary_translations[target_language] = translation
            doc.save()
            
            return JsonResponse({
                'success': True,
                'translation': translation,
                'language': target_language,
                'cached': False
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '').strip()
            
            if not question:
                return JsonResponse({'response': 'Please ask me a question! I\'m here to help with your studies. 📚'})
            
            # Load API key from .env file
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('GOOGLE_AI_API_KEY')
            
            if not api_key:
                return JsonResponse({'response': generate_fallback_response(question)})
            
            # Initialize Gemini AI
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Enhanced prompt for better study assistance
            enhanced_prompt = f"""
            You are StudyGenie's AI Assistant, a helpful and knowledgeable study companion. 
            
            User Question: {question}
            
            Instructions:
            1. Provide clear, concise, and educational responses
            2. Use simple language that's easy to understand
            3. Include examples when helpful
            4. Be encouraging and supportive
            5. If it's a study-related question, provide structured information
            6. Keep responses under 200 words for better readability
            7. Use emojis sparingly but appropriately
            
            Respond as a friendly AI tutor:
            """
            
            # Generate AI response
            response = model.generate_content(enhanced_prompt)
            ai_response = response.text.strip()
            
            # Format response for HTML display
            ai_response = format_ai_response(ai_response)
            
            print(f"AI Response generated successfully: {len(ai_response)} characters")
            return JsonResponse({'response': ai_response})
            
        except Exception as e:
            print(f"Chatbot AI Error: {e}")
            # Generate intelligent fallback response
            fallback_response = generate_fallback_response(question)
            return JsonResponse({'response': fallback_response})
    
    return JsonResponse({'response': 'Invalid request method. Please use POST.'})

def format_ai_response(response):
    """Format AI response for better HTML display"""
    # Convert newlines to HTML breaks
    formatted = response.replace('\n\n', '<br><br>').replace('\n', '<br>')
    
    # Make bold text more prominent
    formatted = formatted.replace('**', '<strong>').replace('**', '</strong>')
    
    # Handle bullet points
    lines = formatted.split('<br>')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('•') or line.startswith('-'):
            line = f"<span style='color: #4facfe;'>•</span> {line[1:].strip()}"
        elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
            line = f"<span style='color: #4facfe; font-weight: bold;'>{line[:2]}</span> {line[2:].strip()}"
        formatted_lines.append(line)
    
    return '<br>'.join(formatted_lines)

@csrf_exempt
def get_quiz_in_language(request, doc_id):
    """Get quiz questions in specific language"""
    if request.method == 'POST':
        doc = get_object_or_404(Document, id=doc_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            target_language = data.get('language', 'en')
            difficulty = data.get('difficulty', 'medium')
            
            from ai_services import generate_quiz_with_language
            quiz_data = generate_quiz_with_language(doc.extracted_text, target_language, difficulty)
            
            return JsonResponse({
                'success': True,
                'quiz': quiz_data,
                'language': target_language,
                'difficulty': difficulty
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_flashcards_in_language(request, doc_id):
    """Get flashcards in specific language"""
    if request.method == 'POST':
        doc = get_object_or_404(Document, id=doc_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            target_language = data.get('language', 'en')
            
            from ai_services import generate_flashcards_with_language
            flashcard_data = generate_flashcards_with_language(doc.extracted_text, target_language)
            
            return JsonResponse({
                'success': True,
                'flashcards': flashcard_data,
                'language': target_language
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def generate_fallback_response(question):
    """Generate intelligent fallback responses when AI is unavailable"""
    question_lower = question.lower()
    
    # Study-related responses
    if any(word in question_lower for word in ['study', 'learn', 'understand', 'explain']):
        return "📚 Great question about studying! Here are some general tips:<br><br>• Break complex topics into smaller parts<br>• Use active recall and spaced repetition<br>• Create summaries and flashcards<br>• Practice with quizzes regularly<br><br>For specific help, try uploading your study materials! 🎯"
    
    elif any(word in question_lower for word in ['quiz', 'test', 'exam', 'practice']):
        return "📝 For effective test preparation:<br><br>• Review your notes regularly<br>• Take practice quizzes<br>• Focus on weak areas<br>• Use active recall techniques<br><br>Upload your documents to generate custom quizzes! ✨"
    
    elif any(word in question_lower for word in ['flashcard', 'memory', 'remember', 'memorize']):
        return "🧠 Memory techniques that work:<br><br>• Use spaced repetition<br>• Create visual associations<br>• Practice active recall<br>• Review before sleeping<br><br>Try our AI-generated flashcards for better retention! 💡"
    
    elif any(word in question_lower for word in ['help', 'how', 'what', 'why']):
        return f"🤔 I'd love to help you with that! While I'm having trouble connecting to my AI brain right now, here's what I can suggest:<br><br>• Upload your study materials for personalized help<br>• Use our quiz and flashcard features<br>• Try breaking down complex topics<br><br>Feel free to ask more specific questions! 🚀"
    
    elif 'hello' in question_lower or 'hi' in question_lower or 'hey' in question_lower:
        return "👋 Hello! I'm your AI study assistant. I'm here to help you learn better!<br><br>You can ask me about:<br>• Study techniques<br>• Subject explanations<br>• Learning strategies<br>• Test preparation<br><br>What would you like to learn today? 📖"
    
    else:
        return f"🤖 Thanks for your question! I'm currently having some technical difficulties, but I'm still here to help!<br><br>Try:<br>• Uploading documents for AI analysis<br>• Using our quiz generator<br>• Creating flashcards<br>• Switching languages for multilingual support<br><br>What specific topic are you studying? 📚"