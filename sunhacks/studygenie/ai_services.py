import google.generativeai as genai
import json
import os
from django.conf import settings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Google AI (Gemini) client
try:
    # Get API key from environment variables
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    
    if not api_key:
        # Fallback to Django settings
        try:
            api_key = getattr(settings, 'GOOGLE_AI_API_KEY', None)
        except:
            pass
    
    if not api_key or api_key == 'your-google-ai-key':
        print("WARNING: Google AI API key not configured properly")
        print("Please set GOOGLE_AI_API_KEY in your .env file")
        print("Current .env file should contain: GOOGLE_AI_API_KEY=your_actual_api_key")
        client = None
    else:
        print(f"Initializing Google AI with API key: {api_key[:10]}...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        client = model
        print("Google AI client initialized successfully")
except Exception as e:
    print(f"Google AI client initialization error: {e}")
    print("Make sure you have installed: pip install python-dotenv google-generativeai")
    client = None

def detect_language(text):
    """Detect the primary language of the text"""
    if not text:
        return 'en'
    
    # Check for Devanagari script (Hindi/Marathi)
    devanagari_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
    total_chars = len([char for char in text if char.isalpha()])
    
    if total_chars > 0 and (devanagari_chars / total_chars) > 0.3:
        # Check for Marathi-specific words
        marathi_words = ['आहे', 'होते', 'करणे', 'असे', 'त्या', 'त्यांना', 'मराठी', 'महाराष्ट्र', 'मुंबई', 'पुणे']
        hindi_words = ['है', 'था', 'करना', 'ऐसे', 'उन', 'उनको', 'हिंदी', 'भारत', 'दिल्ली', 'मुंबई']
        
        marathi_count = sum(1 for word in marathi_words if word in text)
        hindi_count = sum(1 for word in hindi_words if word in text)
        
        if marathi_count > hindi_count:
            return 'mr'
        else:
            return 'hi'
    
    return 'en'  # Default to English

def get_language_prompt(language):
    """Get language-specific prompts for English, Hindi, and Marathi"""
    prompts = {
        'english': {
            'summary': 'Write a comprehensive summary in English',
            'quiz': 'Create quiz questions in English',
            'flashcards': 'Create flashcards in English'
        },
        'hindi': {
            'summary': 'हिंदी में एक व्यापक सारांश लिखें',
            'quiz': 'हिंदी में प्रश्नोत्तरी के प्रश्न बनाएं',
            'flashcards': 'हिंदी में फ्लैशकार्ड बनाएं'
        },
        'marathi': {
            'summary': 'मराठीत एक सर्वसमावेशक सारांश लिहा',
            'quiz': 'मराठीत प्रश्नमंजुषा प्रश्न तयार करा',
            'flashcards': 'मराठीत फ्लॅशकार्ड तयार करा'
        }
    }
    return prompts.get(language, prompts['english'])

def extract_technical_keywords(text, top_n=5):
    """Extract precise technical keywords for YouTube search"""
    if not text:
        return []
    
    import re
    from collections import Counter
    
    # Clean text but preserve technical terms
    text = re.sub(r'[^a-zA-Z0-9\s\-]', ' ', text)
    
    # Enhanced stop words (more comprehensive)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'document', 'summary', 'content', 'material', 'information', 'text', 'study', 'learning',
        'chapter', 'section', 'page', 'book', 'pdf', 'file', 'contains', 'includes', 'covers',
        'discusses', 'explains', 'describes', 'shows', 'presents', 'provides', 'important',
        'key', 'main', 'basic', 'essential', 'fundamental', 'concept', 'concepts', 'topic', 'topics'
    }
    
    # Extract multi-word technical terms (e.g., "pin diagram", "8085 microprocessor")
    phrases = []
    words = text.split()
    
    # Look for technical phrases (2-3 words)
    for i in range(len(words) - 1):
        if len(words[i]) > 2 and len(words[i+1]) > 2:
            phrase = f"{words[i].lower()} {words[i+1].lower()}"
            if not any(stop in phrase for stop in stop_words):
                phrases.append(phrase)
    
    # Extract single technical words
    single_words = []
    for word in words:
        word_clean = word.lower().strip()
        if (len(word_clean) > 3 and 
            word_clean not in stop_words and 
            word_clean.isalnum() and
            not word_clean.isdigit()):
            single_words.append(word_clean)
    
    # Prioritize technical terms (numbers, technical words)
    priority_keywords = []
    for word in words:
        word_clean = word.strip()
        # Technical numbers/codes (e.g., 8085, VCC, VSS)
        if (len(word_clean) >= 2 and 
            (word_clean.isdigit() or 
             any(char.isdigit() for char in word_clean) or
             word_clean.isupper())):
            priority_keywords.append(word_clean.lower())
    
    # Count frequencies
    phrase_counts = Counter(phrases)
    word_counts = Counter(single_words)
    priority_counts = Counter(priority_keywords)
    
    # Combine results with priority
    final_keywords = []
    
    # Add priority technical terms first
    for keyword, count in priority_counts.most_common(2):
        if keyword not in final_keywords:
            final_keywords.append(keyword)
    
    # Add top phrases
    for phrase, count in phrase_counts.most_common(2):
        if phrase not in final_keywords and len(final_keywords) < top_n:
            final_keywords.append(phrase)
    
    # Fill remaining with single words
    for word, count in word_counts.most_common(top_n):
        if word not in final_keywords and len(final_keywords) < top_n:
            final_keywords.append(word)
    
    return final_keywords[:top_n]

def generate_summary_with_ai(text, length="medium"):
    """Generate highly relevant, document-specific summary"""
    if not client:
        return generate_smart_fallback_summary(text)
    
    if not text or len(text.strip()) < 10:
        return "Insufficient text content for summary generation."
    
    try:
        # Extract key information from document first
        key_terms = extract_key_terms_from_text(text)
        main_topics = extract_main_topics(text)
        document_type = detect_document_type(text)
        
        prompt = f"""
        Create a comprehensive, well-structured summary of this document following these EXACT formatting requirements:
        
        DOCUMENT ANALYSIS:
        - Document Type: {document_type}
        - Key Terms: {', '.join(key_terms[:10])}
        - Main Topics: {', '.join(main_topics[:5])}
        
        FORMATTING REQUIREMENTS:
        1. Length: 100-150 words total
        2. Structure: Introduction paragraph + Key Points in bullet format
        3. Start with: "This document covers [specific topic]..."
        4. Follow with: "\n\nKey Points:\n• [Point 1]\n• [Point 2]\n• [Point 3]\n• [Point 4]"
        5. Use ACTUAL terms and concepts from the document
        6. Make each bullet point specific and informative (10-15 words each)
        7. Include specific details: numbers, formulas, procedures, examples from text
        
        CONTENT REQUIREMENTS:
        - Use ONLY information from the provided document
        - Mention specific technical terms, definitions, procedures
        - Include concrete examples or applications mentioned
        - Be precise about what the document teaches
        
        DOCUMENT CONTENT:
        {text[:5000]}
        
        Generate a summary that clearly shows what specific knowledge this document contains.
        """
        
        response = client.generate_content(prompt)
        result = response.text.strip()
        
        # Validate and format the summary
        if result and len(result.strip()) > 100:
            formatted_result = format_structured_summary(result)
            if is_summary_well_formatted(formatted_result, key_terms):
                return formatted_result
            else:
                print("AI summary not well formatted, using enhanced fallback")
                return generate_enhanced_fallback_summary(text, key_terms, main_topics)
        else:
            print("AI summary too short, using enhanced fallback")
            return generate_enhanced_fallback_summary(text, key_terms, main_topics)
            
    except Exception as e:
        print(f"AI summary error: {e}")
        key_terms = extract_key_terms_from_text(text)
        main_topics = extract_main_topics(text)
        return generate_enhanced_fallback_summary(text, key_terms, main_topics)

def format_structured_summary(summary_text):
    """Format summary with proper structure and bullet points"""
    # Remove redundant phrases
    redundant_phrases = [
        'as mentioned', 'as stated', 'as discussed', 'as we can see',
        'it is important to note', 'it should be noted', 'furthermore',
        'in addition', 'moreover', 'additionally', 'also mentioned'
    ]
    
    for phrase in redundant_phrases:
        summary_text = summary_text.replace(phrase, '')
    
    # Clean up the text
    summary_text = ' '.join(summary_text.split())
    
    # If already well-formatted with bullet points, return as is
    if '\n•' in summary_text or '\n- ' in summary_text:
        return summary_text
    
    # If it has markdown bullets, convert them
    if '**' in summary_text or '- ' in summary_text:
        lines = [line.strip() for line in summary_text.split('\n') if line.strip()]
        formatted_lines = []
        
        for line in lines:
            if line.startswith('- '):
                formatted_lines.append(f"• {line[2:].strip()}")
            elif line.startswith('**') and line.endswith('**'):
                # Skip markdown headers
                continue
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    return summary_text

def is_summary_well_formatted(summary, key_terms):
    """Check if summary is well-formatted with proper structure"""
    if not summary or len(summary) < 100:
        return False
    
    # Check for proper structure (intro + bullet points)
    has_bullets = ('•' in summary or '- ' in summary)
    has_key_terms = sum(1 for term in key_terms[:5] if term.lower() in summary.lower()) >= 2
    has_good_length = 100 <= len(summary) <= 200
    
    return has_bullets and has_key_terms and has_good_length

def generate_summary_with_language(text, language, length="medium"):
    """Generate brief, comprehensive summary in specific language"""
    if not client:
        return f"Summary of the document content in {language}. The document contains educational material that can be studied and reviewed."
    
    try:
        language_names = {
            'en': 'English',
            'hi': 'Hindi',
            'mr': 'Marathi', 
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German'
        }
        
        lang_name = language_names.get(language, 'English')
        
        prompt = f"""
        Create a comprehensive summary in {lang_name} based on the document content below.
        
        REQUIREMENTS:
        - Write entirely in {lang_name}
        - Maximum 150 words
        - Use ONLY information from the document
        - Include key concepts and important details
        - Make it educational and informative
        
        DOCUMENT CONTENT:
        {text[:3000]}
        
        Write the summary in {lang_name}:
        """
        
        response = client.generate_content(prompt)
        result = response.text.strip()
        return result if result else f"Summary generated in {lang_name}"
    except Exception as e:
        return f"Summary of the document content in {language_names.get(language, 'English')}. The document contains educational material."



def generate_quiz_with_language(text, language='en', difficulty='medium'):
    """Generate quiz questions in specific language"""
    if not client:
        return [{
            "stem": f"What is the main topic of this document?",
            "options": {"A": "Educational content", "B": "Random text", "C": "News article", "D": "Fiction"},
            "answer_key": "A",
            "explanation": "This document contains educational material",
            "difficulty": difficulty,
            "language": language
        }]
    
    language_names = {
        'en': 'English',
        'hi': 'Hindi', 
        'mr': 'Marathi',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German'
    }
    
    lang_name = language_names.get(language, 'English')
    
    try:
        prompt = f"""
        Create 5 quiz questions in {lang_name} based on the document content.
        
        REQUIREMENTS:
        - Write questions entirely in {lang_name}
        - Difficulty: {difficulty}
        - Use document information only
        - Include 4 options (A, B, C, D)
        - Provide correct answer
        
        DOCUMENT:
        {text[:2000]}
        
        Format as JSON array:
        [
            {{
                "stem": "Question in {lang_name}?",
                "options": {{"A": "Option 1", "B": "Option 2", "C": "Option 3", "D": "Option 4"}},
                "answer_key": "A",
                "explanation": "Explanation in {lang_name}",
                "difficulty": "{difficulty}",
                "language": "{language}"
            }}
        ]
        """
        
        response = client.generate_content(prompt)
        content = response.text.strip()
        
        # Try to extract JSON
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end != 0:
            json_str = content[start:end]
            result = json.loads(json_str)
            return result[:5]  # Return up to 5 questions
        else:
            # Fallback if JSON parsing fails
            return [{
                "stem": f"What is discussed in this document?",
                "options": {"A": "Educational content", "B": "Random information", "C": "News", "D": "Fiction"},
                "answer_key": "A", 
                "explanation": "The document contains educational material",
                "difficulty": difficulty,
                "language": language
            }]
            
    except Exception as e:
        print(f"Quiz generation error: {e}")
        return [{
            "stem": f"What type of content is this?",
            "options": {"A": "Study material", "B": "Entertainment", "C": "News", "D": "Fiction"},
            "answer_key": "A",
            "explanation": "This is educational study material",
            "difficulty": difficulty,
            "language": language
        }]

def generate_quiz_with_ai(text, difficulty='medium'):
    """Generate dynamic quiz questions from document content with distinct difficulty levels"""
    
    if not text or len(text.strip()) < 50:
        return generate_fallback_quiz(text, difficulty)
    
    # Extract key information from document
    key_terms = extract_key_terms_from_text(text)
    main_topics = extract_main_topics(text)
    doc_type = detect_document_type(text)
    
    # Enhanced difficulty-specific instructions
    difficulty_specs = {
        'easy': {
            'cognitive_level': 'Remember and Understand',
            'question_types': ['What is...?', 'Define...', 'Which of the following...?', 'True or False:', 'Identify...'],
            'focus': 'Direct recall, basic definitions, simple identification',
            'distractors': 'Obviously incorrect options',
            'examples': 'Memorization of facts, terminology, basic concepts'
        },
        'medium': {
            'cognitive_level': 'Apply and Analyze', 
            'question_types': ['How would...?', 'What happens when...?', 'Compare...', 'Explain why...', 'What is the result of...?'],
            'focus': 'Application of concepts, cause-effect relationships, comparisons',
            'distractors': 'Plausible but incorrect options',
            'examples': 'Using knowledge in new situations, understanding relationships'
        },
        'hard': {
            'cognitive_level': 'Evaluate and Create',
            'question_types': ['Analyze...', 'Evaluate...', 'What would be the best...?', 'Critique...', 'Design...'],
            'focus': 'Critical thinking, evaluation, synthesis, complex reasoning',
            'distractors': 'Very plausible options requiring deep understanding',
            'examples': 'Making judgments, creating solutions, complex analysis'
        }
    }
    
    spec = difficulty_specs[difficulty]
    
    prompt = f"""
    Generate EXACTLY 10 dynamic {difficulty.upper()} level quiz questions from this specific document content.
    
    DOCUMENT ANALYSIS:
    - Type: {doc_type}
    - Key Terms: {', '.join(key_terms[:8])}
    - Main Topics: {', '.join(main_topics[:5])}
    
    {difficulty.upper()} LEVEL SPECIFICATIONS:
    - Cognitive Level: {spec['cognitive_level']}
    - Question Types: {', '.join(spec['question_types'])}
    - Focus: {spec['focus']}
    - Distractors: {spec['distractors']}
    
    CRITICAL REQUIREMENTS:
    1. Generate EXACTLY 10 questions - no more, no less
    2. Extract content DIRECTLY from the document below
    3. Use ACTUAL terms, concepts, and information from the text
    4. Create {difficulty}-appropriate cognitive challenges
    5. Each question must test different aspects of the content
    6. Include specific details, numbers, names from the document
    7. Make distractors appropriate for {difficulty} level
    
    DOCUMENT CONTENT:
    {text[:5000]}
    
    Generate exactly 10 questions that test {spec['cognitive_level']} of this specific content.
    
    Return ONLY valid JSON array with exactly 10 objects:
    [
        {{
            "stem": "Question based on document content?",
            "options": {{"A": "Option 1", "B": "Option 2", "C": "Option 3", "D": "Option 4"}},
            "answer_key": "A",
            "explanation": "Explanation with reference to document content",
            "difficulty": "{difficulty}",
            "topic": "Specific topic from document"
        }},
        ... (repeat for exactly 10 questions)
    ]
    """
    
    if not client:
        return generate_dynamic_fallback_quiz(text, difficulty, key_terms, main_topics)
        
    try:
        response = client.generate_content(prompt)
        content = response.text.strip()
        
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end != 0:
            json_str = content[start:end]
            result = json.loads(json_str)
            
            # Validate questions are appropriate for difficulty and ensure exactly 10
            validated_result = validate_quiz_difficulty(result, difficulty, key_terms)
            
            # Ensure exactly 10 questions
            if len(validated_result) < 10:
                # Add fallback questions to reach 10
                fallback_questions = generate_dynamic_fallback_quiz(text, difficulty, key_terms, main_topics)
                validated_result.extend(fallback_questions[len(validated_result):10])
            
            return validated_result[:10]  # Ensure exactly 10 questions
        else:
            raise ValueError("No valid JSON found in response")
            
    except Exception as e:
        print(f"AI quiz generation error: {e}")
        return generate_dynamic_fallback_quiz(text, difficulty, key_terms, main_topics)

def generate_dynamic_fallback_quiz(text, difficulty, key_terms, main_topics):
    """Generate dynamic fallback quiz based on actual document content and difficulty"""
    
    questions = []
    
    # Extract content-specific information
    sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if len(s.strip()) > 20]
    doc_type = detect_document_type(text)
    
    # Generate questions based on difficulty and actual content
    if difficulty == 'easy':
        questions.extend(generate_easy_questions(text, key_terms, main_topics, sentences))
    elif difficulty == 'medium':
        questions.extend(generate_medium_questions(text, key_terms, main_topics, sentences))
    else:  # hard
        questions.extend(generate_hard_questions(text, key_terms, main_topics, sentences))
    
    # Ensure we have exactly 10 questions
    while len(questions) < 10:
        generic_q = generate_generic_questions(difficulty, doc_type)
        questions.extend(generic_q)
        if len(questions) >= 10:
            break
    
    return questions[:10]  # Always return exactly 10 questions

def generate_easy_questions(text, key_terms, main_topics, sentences):
    """Generate easy (factual/recall) questions from document content"""
    questions = []
    
    # Definition-based questions from key terms
    for term in key_terms[:3]:
        # Find sentences that define this term
        definition_sentences = [s for s in sentences if term.lower() in s.lower() and 
                              any(word in s.lower() for word in ['is', 'are', 'means', 'refers'])]
        
        if definition_sentences:
            questions.append({
                "stem": f"What is {term}?",
                "options": {
                    "A": definition_sentences[0][:60] + "...",
                    "B": "A type of software application",
                    "C": "A mathematical formula",
                    "D": "A historical event"
                },
                "answer_key": "A",
                "explanation": f"According to the document: {definition_sentences[0][:100]}...",
                "difficulty": "easy",
                "topic": term
            })
    
    # Topic identification questions
    if main_topics:
        questions.append({
            "stem": "What is the main topic covered in this document?",
            "options": {
                "A": main_topics[0] if main_topics else "General concepts",
                "B": "Cooking recipes",
                "C": "Sports statistics",
                "D": "Weather patterns"
            },
            "answer_key": "A",
            "explanation": f"The document primarily focuses on {main_topics[0] if main_topics else 'educational concepts'}.",
            "difficulty": "easy",
            "topic": "Main Topic"
        })
    
    return questions

def generate_medium_questions(text, key_terms, main_topics, sentences):
    """Generate medium (application/analysis) questions from document content"""
    questions = []
    
    # Application-based questions
    for term in key_terms[:2]:
        # Find sentences about applications or uses
        app_sentences = [s for s in sentences if term.lower() in s.lower() and 
                        any(word in s.lower() for word in ['used', 'application', 'example', 'practice'])]
        
        if app_sentences:
            questions.append({
                "stem": f"How is {term} typically used or applied?",
                "options": {
                    "A": app_sentences[0][:60] + "...",
                    "B": "Only for theoretical purposes",
                    "C": "Exclusively in research labs",
                    "D": "Not applicable in practice"
                },
                "answer_key": "A",
                "explanation": f"The document explains: {app_sentences[0][:100]}...",
                "difficulty": "medium",
                "topic": f"{term} Application"
            })
    
    # Process/procedure questions
    process_sentences = [s for s in sentences if any(word in s.lower() for word in 
                        ['process', 'method', 'procedure', 'steps', 'algorithm'])]
    
    if process_sentences:
        questions.append({
            "stem": "What process or method is described in the document?",
            "options": {
                "A": process_sentences[0][:60] + "...",
                "B": "Random trial and error",
                "C": "No specific method mentioned",
                "D": "Only theoretical approaches"
            },
            "answer_key": "A",
            "explanation": f"The document describes: {process_sentences[0][:100]}...",
            "difficulty": "medium",
            "topic": "Process/Method"
        })
    
    return questions

def generate_hard_questions(text, key_terms, main_topics, sentences):
    """Generate hard (evaluation/synthesis) questions from document content"""
    questions = []
    
    # Analysis questions combining multiple concepts
    if len(key_terms) >= 2:
        questions.append({
            "stem": f"Analyze the relationship between {key_terms[0]} and {key_terms[1]} based on the document.",
            "options": {
                "A": "They are complementary concepts that work together",
                "B": "They are completely unrelated",
                "C": "One replaces the other entirely",
                "D": "They are identical concepts"
            },
            "answer_key": "A",
            "explanation": f"The document discusses both {key_terms[0]} and {key_terms[1]} as related concepts.",
            "difficulty": "hard",
            "topic": "Concept Relationships"
        })
    
    # Evaluation questions
    if main_topics:
        questions.append({
            "stem": f"Evaluate the significance of {main_topics[0]} in the broader context described in the document.",
            "options": {
                "A": "It provides foundational understanding for advanced concepts",
                "B": "It has no practical relevance",
                "C": "It only applies to historical contexts",
                "D": "It contradicts established principles"
            },
            "answer_key": "A",
            "explanation": f"The document presents {main_topics[0]} as fundamental to understanding the subject matter.",
            "difficulty": "hard",
            "topic": "Concept Evaluation"
        })
    
    # Synthesis questions
    questions.append({
        "stem": "Based on the document content, what would be the best approach to master this material?",
        "options": {
            "A": "Understand core concepts, practice applications, and analyze relationships",
            "B": "Memorize all details without understanding",
            "C": "Focus only on definitions",
            "D": "Skip complex parts entirely"
        },
        "answer_key": "A",
        "explanation": "Effective mastery requires understanding, application, and analysis as demonstrated in the document.",
        "difficulty": "hard",
        "topic": "Learning Strategy"
    })
    
    return questions

def generate_generic_questions(difficulty, doc_type):
    """Generate generic questions to fill remaining slots"""
    generic_questions = {
        'easy': [
            {
                "stem": f"What type of material is this document?",
                "options": {"A": doc_type, "B": "Fiction novel", "C": "Recipe collection", "D": "Phone directory"},
                "answer_key": "A",
                "explanation": f"This is {doc_type.lower()}.",
                "difficulty": "easy",
                "topic": "Document Type"
            },
            {
                "stem": "What is the primary purpose of studying this material?",
                "options": {"A": "To gain knowledge and understanding", "B": "For entertainment only", "C": "To waste time", "D": "No specific purpose"},
                "answer_key": "A",
                "explanation": "Educational materials are designed to impart knowledge and understanding.",
                "difficulty": "easy",
                "topic": "Learning Purpose"
            },
            {
                "stem": "How should you approach reading this document?",
                "options": {"A": "Carefully and attentively", "B": "Quickly without focus", "C": "Skip most sections", "D": "Read only the title"},
                "answer_key": "A",
                "explanation": "Careful and attentive reading leads to better comprehension.",
                "difficulty": "easy",
                "topic": "Reading Strategy"
            }
        ],
        'medium': [
            {
                "stem": "How should you approach studying this type of material?",
                "options": {"A": "Active reading and understanding", "B": "Passive memorization", "C": "Skip difficult sections", "D": "Read only once"},
                "answer_key": "A",
                "explanation": "Active engagement leads to better understanding and retention.",
                "difficulty": "medium",
                "topic": "Study Strategy"
            },
            {
                "stem": "What is the best way to retain information from this document?",
                "options": {"A": "Take notes and review regularly", "B": "Read once and forget", "C": "Memorize without understanding", "D": "Avoid taking notes"},
                "answer_key": "A",
                "explanation": "Note-taking and regular review enhance retention and understanding.",
                "difficulty": "medium",
                "topic": "Retention Strategy"
            },
            {
                "stem": "How can you test your understanding of this material?",
                "options": {"A": "Practice questions and self-assessment", "B": "Avoid any testing", "C": "Only read passively", "D": "Skip review sessions"},
                "answer_key": "A",
                "explanation": "Practice questions and self-assessment help identify knowledge gaps.",
                "difficulty": "medium",
                "topic": "Self-Assessment"
            }
        ],
        'hard': [
            {
                "stem": "Evaluate the most effective way to apply knowledge from this document.",
                "options": {"A": "Practice, analyze, and synthesize concepts", "B": "Memorize without application", "C": "Use only in exams", "D": "Avoid practical use"},
                "answer_key": "A",
                "explanation": "True mastery comes from practical application and synthesis of knowledge.",
                "difficulty": "hard",
                "topic": "Knowledge Application"
            },
            {
                "stem": "Analyze the best approach to master complex concepts in this material.",
                "options": {"A": "Break down into smaller parts and build understanding", "B": "Memorize everything at once", "C": "Ignore difficult concepts", "D": "Rely only on surface-level reading"},
                "answer_key": "A",
                "explanation": "Breaking complex concepts into smaller parts facilitates deeper understanding.",
                "difficulty": "hard",
                "topic": "Complex Learning"
            },
            {
                "stem": "Critique the importance of connecting this material to real-world applications.",
                "options": {"A": "Essential for meaningful learning and retention", "B": "Unnecessary for academic success", "C": "Only relevant for practical subjects", "D": "Should be avoided completely"},
                "answer_key": "A",
                "explanation": "Connecting academic material to real-world applications enhances understanding and retention.",
                "difficulty": "hard",
                "topic": "Application Connection"
            }
        ]
    }
    
    return generic_questions.get(difficulty, generic_questions['medium'])

def validate_quiz_difficulty(questions, difficulty, key_terms):
    """Validate that questions match the intended difficulty level"""
    validated_questions = []
    
    for q in questions:
        # Ensure question has required fields
        if not all(key in q for key in ['stem', 'options', 'answer_key', 'explanation']):
            continue
            
        # Add difficulty and topic if missing
        if 'difficulty' not in q:
            q['difficulty'] = difficulty
        if 'topic' not in q:
            q['topic'] = 'General'
            
        # Validate question complexity matches difficulty
        stem = q['stem'].lower()
        
        if difficulty == 'easy':
            # Easy questions should be factual/recall
            if any(word in stem for word in ['what is', 'define', 'which', 'identify']):
                validated_questions.append(q)
        elif difficulty == 'medium':
            # Medium questions should be application/analysis
            if any(word in stem for word in ['how', 'why', 'compare', 'explain', 'what happens']):
                validated_questions.append(q)
        else:  # hard
            # Hard questions should be evaluation/synthesis
            if any(word in stem for word in ['analyze', 'evaluate', 'critique', 'synthesize', 'best approach']):
                validated_questions.append(q)
        
        # If validation fails, still include but mark appropriately
        if q not in validated_questions:
            validated_questions.append(q)
    
    # Ensure we have exactly 10 questions
    while len(validated_questions) < 10:
        generic_q = generate_generic_questions(difficulty, 'Educational Material')
        for q in generic_q:
            if len(validated_questions) < 10:
                validated_questions.append(q)
    
    return validated_questions[:10]

def generate_flashcards_with_language(text, language='en'):
    """Generate flashcards in specific language"""
    if not client:
        return [{"front": "Key concept", "back": "Important information from document", "language": language}]
    
    language_names = {
        'en': 'English',
        'hi': 'Hindi',
        'mr': 'Marathi', 
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German'
    }
    
    lang_name = language_names.get(language, 'English')
    
    try:
        prompt = f"""
        Create 5 flashcards in {lang_name} based on the document content.
        
        REQUIREMENTS:
        - Write entirely in {lang_name}
        - Front: Short term/question (max 8 words)
        - Back: Brief answer (max 20 words)
        - Use document information only
        
        DOCUMENT:
        {text[:2000]}
        
        Format as JSON:
        [
            {{
                "front": "Term in {lang_name}",
                "back": "Definition in {lang_name}",
                "language": "{language}"
            }}
        ]
        """
        
        response = client.generate_content(prompt)
        content = response.text.strip()
        
        # Try to extract JSON
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end != 0:
            json_str = content[start:end]
            result = json.loads(json_str)
            return result[:5]  # Return up to 5 flashcards
        else:
            # Fallback
            return [{
                "front": "Main topic",
                "back": "Key educational content from document",
                "language": language
            }]
            
    except Exception as e:
        print(f"Flashcard generation error: {e}")
        return [{
            "front": "Document content",
            "back": "Educational material for study",
            "language": language
        }]

def generate_flashcards_with_ai(text):
    """Generate concise, precise flashcards for revision"""
    if not client:
        return generate_fallback_flashcards(text)
    
    prompt = f"""
    Create precise flashcards for quick revision. Extract key terms and concepts from the document.
    
    STRICT REQUIREMENTS:
    - Front: Single term, keyword, or short question (max 10 words)
    - Back: Concise definition or answer (1-2 lines max, under 25 words)
    - Focus on key terms, definitions, and important concepts
    - NO long paragraphs or detailed explanations
    - Make them suitable for quick memorization
    
    DOCUMENT CONTENT:
    {text[:3000]}
    
    Return ONLY valid JSON:
    [
        {{
            "front": "Term or short question",
            "back": "Brief definition (1-2 lines)"
        }}
    ]
    
    Generate 8-12 flashcards.
    """
    
    try:
        pass
        response = client.generate_content(prompt)
        content = response.text.strip()
        pass
        
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end != 0:
            json_str = content[start:end]
            result = json.loads(json_str)
            pass
            return result
        else:
            raise ValueError("No valid JSON found")
            
    except Exception as e:
        pass
        return generate_fallback_flashcards(text)

def translate_content(text, target_language):
    """Translate content to target language"""
    if not client or not text:
        return text
    
    try:
        language_names = {
            'hi': 'Hindi',
            'mr': 'Marathi',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'en': 'English'
        }
        
        lang_name = language_names.get(target_language, 'English')
        
        prompt = f"""
        Translate the following text to {lang_name}. Keep the meaning and educational content intact.
        
        Original text:
        {text[:2000]}
        
        Translate to {lang_name}:
        """
        
        response = client.generate_content(prompt)
        result = response.text.strip()
        return result if result else text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def generate_fallback_flashcards(text):
    """Generate concept-based fallback flashcards from document content"""
    if not text or len(text.strip()) < 50:
        return [
            {"front": "What is the main topic?", "back": "Key educational concept from the material."},
            {"front": "Important term", "back": "Definition and explanation."},
            {"front": "Key principle", "back": "Fundamental rule or concept."}
        ]
    
    detected_lang = detect_language(text)
    flashcards = []
    
    # Extract concepts from document content
    lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 20]
    sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if len(s.strip()) > 15]
    
    # Find definition-like sentences
    definition_keywords = ['is', 'are', 'means', 'refers to', 'defined as', 'known as', 'called']
    concept_sentences = []
    
    for sentence in sentences[:20]:  # Check first 20 sentences
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in definition_keywords):
            concept_sentences.append(sentence)
    
    # Create flashcards from concepts found
    for i, sentence in enumerate(concept_sentences[:10]):
        words = sentence.split()
        if len(words) > 5:
            # Try to extract the main concept
            concept_word = None
            for word in words[:5]:  # Look in first 5 words
                if len(word) > 3 and word.lower() not in ['the', 'this', 'that', 'these', 'those', 'and', 'but', 'for']:
                    concept_word = word.strip('.,!?;:')
                    break
            
            if concept_word:
                if detected_lang == 'hindi':
                    flashcards.append({
                        "front": f"{concept_word} क्या है?",
                        "back": sentence[:100] + "..." if len(sentence) > 100 else sentence
                    })
                elif detected_lang == 'marathi':
                    flashcards.append({
                        "front": f"{concept_word} काय आहे?",
                        "back": sentence[:100] + "..." if len(sentence) > 100 else sentence
                    })
                else:  # English
                    flashcards.append({
                        "front": f"What is {concept_word}?",
                        "back": sentence[:100] + "..." if len(sentence) > 100 else sentence
                    })
    
    # Add topic-based flashcards
    if 'control statements' in text.lower():
        flashcards.extend([
            {"front": "What are control statements?", "back": "Programming constructs that control the flow of execution in code."},
            {"front": "What are the main types of control statements?", "back": "Conditional statements, looping statements, and jump statements."}
        ])
    
    if 'if statement' in text.lower() or 'if-else' in text.lower():
        flashcards.append({
            "front": "What is an if statement?",
            "back": "A conditional statement that executes code based on whether a condition is true or false."
        })
    
    if 'loop' in text.lower():
        flashcards.append({
            "front": "What is a loop?",
            "back": "A programming construct that repeats a block of code multiple times."
        })
    
    # Ensure we have at least 8 flashcards
    while len(flashcards) < 8:
        flashcards.extend([
            {"front": "What is the main topic of this document?", "back": "Educational content covering key concepts and principles."},
            {"front": "Why is this material important?", "back": "It provides fundamental knowledge essential for understanding the subject."},
            {"front": "How should you study this content?", "back": "Focus on understanding concepts, definitions, and their applications."}
        ])
    
    return flashcards[:12]  # Return up to 12 flashcards

def generate_multilingual_content(document, target_languages):
    """Generate content in multiple languages after upload"""
    results = {}
    
    for lang_code in target_languages:
        try:
            # Generate summary in target language
            summary = generate_summary_with_language(document.extracted_text, lang_code)
            document.set_summary_translation(lang_code, summary)
            
            # Generate quiz in target language
            quiz_data = generate_quiz_with_language(document.extracted_text, lang_code)
            
            # Generate flashcards in target language
            flashcard_data = generate_flashcards_with_language(document.extracted_text, lang_code)
            
            results[lang_code] = {
                'summary': summary,
                'quiz': quiz_data,
                'flashcards': flashcard_data,
                'status': 'success'
            }
            
        except Exception as e:
            results[lang_code] = {
                'status': 'error',
                'error': str(e)
            }
    
    return results
    







def extract_key_terms_from_text(text):
    """Extract specific technical terms and concepts from document"""
    import re
    from collections import Counter
    
    if not text:
        return []
    
    # Clean text but preserve technical terms
    text = re.sub(r'[^a-zA-Z0-9\s\-_]', ' ', text)
    words = text.split()
    
    # Enhanced stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'document', 'content', 'material', 'information', 'text', 'chapter', 'section', 'page'
    }
    
    # Extract technical terms (capitalized, numbers, technical patterns)
    key_terms = []
    for word in words:
        word_clean = word.strip().lower()
        if (len(word_clean) > 2 and 
            word_clean not in stop_words and
            (word.isupper() or  # Acronyms like CPU, RAM
             any(char.isdigit() for char in word) or  # Technical codes like 8085
             word_clean in ['programming', 'algorithm', 'function', 'variable', 'loop', 'condition', 'statement'])):
            key_terms.append(word)
    
    # Count frequency and return most common
    term_counts = Counter(key_terms)
    return [term for term, count in term_counts.most_common(15)]

def extract_main_topics(text):
    """Extract main topics and subjects from document"""
    if not text:
        return []
    
    # Look for topic indicators
    topic_patterns = [
        r'chapter \d+[:\-]?\s*([^\n]+)',
        r'unit \d+[:\-]?\s*([^\n]+)',
        r'section \d+[:\-]?\s*([^\n]+)',
        r'topic[:\-]?\s*([^\n]+)',
        r'introduction to ([^\n]+)',
        r'overview of ([^\n]+)'
    ]
    
    topics = []
    import re
    
    for pattern in topic_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        topics.extend([match.strip()[:50] for match in matches])
    
    # If no structured topics found, extract from headings and important sentences
    if not topics:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if (len(line) > 10 and len(line) < 100 and
                (line.isupper() or  # ALL CAPS headings
                 line.count(' ') < 8)):  # Short lines likely to be headings
                topics.append(line)
    
    return topics[:10]

def detect_document_type(text):
    """Detect what type of document this is"""
    if not text:
        return "Educational Document"
    
    text_lower = text.lower()
    
    # Programming/CS documents
    if any(term in text_lower for term in ['programming', 'algorithm', 'code', 'function', 'variable', 'loop', 'java', 'python', 'c++']):
        return "Programming/Computer Science Material"
    
    # Mathematics
    if any(term in text_lower for term in ['equation', 'formula', 'theorem', 'proof', 'mathematics', 'calculus', 'algebra']):
        return "Mathematics Material"
    
    # Physics
    if any(term in text_lower for term in ['physics', 'force', 'energy', 'momentum', 'wave', 'particle', 'quantum']):
        return "Physics Material"
    
    # Engineering
    if any(term in text_lower for term in ['engineering', 'circuit', 'design', 'system', 'microprocessor', 'pin diagram']):
        return "Engineering Material"
    
    # General academic
    if any(term in text_lower for term in ['chapter', 'unit', 'lesson', 'study', 'exam', 'course']):
        return "Academic Study Material"
    
    return "Educational Document"

def is_summary_specific(summary, key_terms):
    """Check if summary contains specific terms from the document"""
    if not summary or not key_terms:
        return False
    
    summary_lower = summary.lower()
    
    # Check if summary contains actual key terms from document
    specific_terms_found = sum(1 for term in key_terms if term.lower() in summary_lower)
    
    # Check for generic phrases that indicate non-specific summary
    generic_phrases = [
        'this document contains', 'provides information about', 'covers various topics',
        'discusses important concepts', 'educational material', 'study material'
    ]
    
    has_generic_phrases = any(phrase in summary_lower for phrase in generic_phrases)
    
    # Summary is specific if it has key terms and minimal generic phrases
    return specific_terms_found >= 2 and not has_generic_phrases

def generate_enhanced_fallback_summary(text, key_terms=None, main_topics=None):
    """Generate well-formatted, comprehensive summary with 100-150 words and bullet points"""
    if not text or len(text.strip()) < 50:
        return "This document contains limited readable content for comprehensive analysis."
    
    if not key_terms:
        key_terms = extract_key_terms_from_text(text)
    if not main_topics:
        main_topics = extract_main_topics(text)
    
    # Clean and process text
    text = text.strip()
    sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if len(s.strip()) > 20]
    
    # Build structured summary with introduction and key points
    doc_type = detect_document_type(text)
    
    # Introduction paragraph (40-60 words)
    if main_topics and main_topics[0]:
        intro = f"This {doc_type.lower()} provides comprehensive coverage of {main_topics[0].lower()}"
    else:
        intro = f"This {doc_type.lower()} covers essential concepts and principles"
    
    # Add context about key areas
    if key_terms:
        intro += f", focusing on {', '.join(key_terms[:3]).lower()} and related technical concepts."
    else:
        intro += " with detailed explanations and practical applications."
    
    # Extract key points for bullet format
    key_points = []
    
    # 1. Look for definitions and core concepts
    definition_sentences = []
    for sentence in sentences[:20]:
        if any(word in sentence.lower() for word in ['is defined as', 'refers to', 'means', 'is called', 'is known as', 'definition']):
            definition_sentences.append(sentence[:80])
    
    if definition_sentences:
        key_points.append(f"Defines key concepts: {definition_sentences[0]}")
    
    # 2. Add technical terms and their significance
    if key_terms:
        if len(key_terms) >= 4:
            key_points.append(f"Covers technical topics including {', '.join(key_terms[:4])}")
        else:
            key_points.append(f"Explores important concepts: {', '.join(key_terms)}")
    
    # 3. Look for procedures, methods, or processes
    process_sentences = []
    for sentence in sentences[:15]:
        if any(word in sentence.lower() for word in ['process', 'method', 'procedure', 'algorithm', 'steps', 'approach']):
            process_sentences.append(sentence[:70])
    
    if process_sentences:
        key_points.append(f"Explains methodologies: {process_sentences[0]}")
    
    # 4. Look for applications or examples
    application_sentences = []
    for sentence in sentences[:15]:
        if any(word in sentence.lower() for word in ['application', 'example', 'used for', 'practice', 'implementation']):
            application_sentences.append(sentence[:70])
    
    if application_sentences:
        key_points.append(f"Provides practical applications: {application_sentences[0]}")
    
    # 5. Add specific content-based points if we don't have enough
    while len(key_points) < 4 and sentences:
        for sentence in sentences[:10]:
            if (len(sentence) > 40 and len(sentence) < 100 and 
                any(term.lower() in sentence.lower() for term in key_terms[:8]) and
                sentence not in [kp.split(': ', 1)[-1] if ': ' in kp else kp for kp in key_points]):
                key_points.append(f"Details: {sentence}")
                break
        break
    
    # Ensure we have at least 3 key points
    if len(key_points) < 3:
        key_points.extend([
            f"Presents structured information on {doc_type.lower().replace('material', 'topics')}",
            f"Includes detailed explanations and technical specifications",
            f"Provides foundational knowledge for understanding the subject matter"
        ])
    
    # Format the final summary
    summary = intro + "\n\nKey Points:"
    for point in key_points[:4]:  # Limit to 4 key points
        summary += f"\n• {point}"
    
    # Ensure proper length (100-150 words)
    word_count = len(summary.split())
    if word_count < 100:
        # Add more detail to existing points
        if main_topics and len(main_topics) > 1:
            summary += f"\n• Additionally covers: {', '.join(main_topics[1:3])}"
        if len(key_terms) > 4:
            summary += f"\n• Advanced topics include: {', '.join(key_terms[4:7])}"
    
    return summary

