"""
Real-time AI Assistant for StudyGenie Dashboard
Provides intelligent study assistance with proper API key handling
"""

import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

class AIAssistant:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_AI_API_KEY')
        self.model = None
        self.initialize_ai()
    
    def initialize_ai(self):
        """Initialize the AI model with proper error handling"""
        try:
            if not self.api_key:
                print("ERROR: GOOGLE_AI_API_KEY not found in environment variables")
                return False
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print(f"AI Assistant initialized successfully with key: {self.api_key[:10]}...")
            return True
        except Exception as e:
            print(f"AI initialization error: {e}")
            return False
    
    def generate_response(self, question, context=None):
        """Generate AI response with enhanced prompting"""
        if not self.model:
            return self.generate_fallback_response(question)
        
        try:
            # Create enhanced prompt based on context
            if context:
                prompt = f"""
                You are StudyGenie's AI Assistant, helping students learn effectively.
                
                Context: {context}
                Student Question: {question}
                
                Provide a helpful, educational response that:
                1. Directly answers the question
                2. Uses simple, clear language
                3. Includes practical examples when relevant
                4. Encourages further learning
                5. Keeps response under 150 words
                
                Response:
                """
            else:
                prompt = f"""
                You are StudyGenie's AI Assistant, a friendly and knowledgeable study companion.
                
                Student Question: {question}
                
                Provide a helpful response that:
                1. Answers the question clearly and concisely
                2. Uses encouraging and supportive tone
                3. Includes actionable study tips when relevant
                4. Suggests using StudyGenie features when appropriate
                5. Keeps response under 150 words
                6. Uses emojis sparingly for engagement
                
                Response:
                """
            
            response = self.model.generate_content(prompt)
            return self.format_response(response.text.strip())
            
        except Exception as e:
            print(f"AI response generation error: {e}")
            return self.generate_fallback_response(question)
    
    def format_response(self, response):
        """Format AI response for better HTML display"""
        # Convert newlines to HTML breaks
        formatted = response.replace('\n\n', '<br><br>').replace('\n', '<br>')
        
        # Handle markdown-style formatting
        formatted = formatted.replace('**', '<strong>').replace('**', '</strong>')
        formatted = formatted.replace('*', '<em>').replace('*', '</em>')
        
        # Format bullet points
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
    
    def generate_fallback_response(self, question):
        """Generate intelligent fallback responses when AI is unavailable"""
        question_lower = question.lower()
        
        # Greeting responses
        if any(word in question_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return """
            👋 Hello! I'm your AI study assistant from StudyGenie!<br><br>
            I can help you with:<br>
            • Study techniques and strategies<br>
            • Subject explanations<br>
            • Test preparation tips<br>
            • Learning optimization<br><br>
            What would you like to learn about today? 📚
            """
        
        # Study-related questions
        elif any(word in question_lower for word in ['study', 'learn', 'understand', 'explain', 'how to']):
            return """
            📚 Great question about studying! Here are some proven techniques:<br><br>
            • <strong>Active Recall:</strong> Test yourself regularly<br>
            • <strong>Spaced Repetition:</strong> Review at increasing intervals<br>
            • <strong>Pomodoro Technique:</strong> 25-min focused sessions<br>
            • <strong>Feynman Method:</strong> Explain concepts simply<br><br>
            Try uploading your documents to get personalized study materials! 🎯
            """
        
        # Memory and retention
        elif any(word in question_lower for word in ['memory', 'remember', 'memorize', 'retention', 'forget']):
            return """
            🧠 Memory enhancement strategies:<br><br>
            • <strong>Chunking:</strong> Break info into smaller pieces<br>
            • <strong>Visual Associations:</strong> Create mental images<br>
            • <strong>Mnemonics:</strong> Use memory aids<br>
            • <strong>Sleep:</strong> Review before bedtime<br><br>
            Our AI-generated flashcards can boost your retention by 40%! 💡
            """
        
        # Test preparation
        elif any(word in question_lower for word in ['test', 'exam', 'quiz', 'preparation', 'practice']):
            return """
            📝 Effective test preparation strategy:<br><br>
            • <strong>Plan Early:</strong> Start 2-3 weeks ahead<br>
            • <strong>Practice Tests:</strong> Simulate exam conditions<br>
            • <strong>Focus Weak Areas:</strong> Identify knowledge gaps<br>
            • <strong>Review Regularly:</strong> Don't cram last minute<br><br>
            Upload your materials to generate custom practice quizzes! ✨
            """
        
        # Time management
        elif any(word in question_lower for word in ['time', 'schedule', 'organize', 'plan', 'manage']):
            return """
            ⏰ Time management for effective studying:<br><br>
            • <strong>Priority Matrix:</strong> Important vs Urgent tasks<br>
            • <strong>Time Blocking:</strong> Dedicate specific hours<br>
            • <strong>Break Schedule:</strong> 50-min study, 10-min break<br>
            • <strong>Weekly Planning:</strong> Set realistic goals<br><br>
            Consistency beats intensity - study regularly! 🚀
            """
        
        # Motivation and productivity
        elif any(word in question_lower for word in ['motivation', 'focus', 'concentrate', 'productive', 'distracted']):
            return """
            🎯 Boost your study motivation and focus:<br><br>
            • <strong>Clear Goals:</strong> Set specific, achievable targets<br>
            • <strong>Environment:</strong> Create a dedicated study space<br>
            • <strong>Rewards:</strong> Celebrate small wins<br>
            • <strong>Accountability:</strong> Study with friends or track progress<br><br>
            Remember: Progress, not perfection! 💪
            """
        
        # Subject-specific help
        elif any(word in question_lower for word in ['math', 'science', 'history', 'english', 'programming', 'physics', 'chemistry']):
            subject = next((word for word in ['math', 'science', 'history', 'english', 'programming', 'physics', 'chemistry'] if word in question_lower), 'your subject')
            return f"""
            📖 Tips for studying {subject}:<br><br>
            • <strong>Understand Concepts:</strong> Don't just memorize<br>
            • <strong>Practice Problems:</strong> Apply what you learn<br>
            • <strong>Connect Ideas:</strong> Link new info to known concepts<br>
            • <strong>Teach Others:</strong> Explain to solidify understanding<br><br>
            Upload your {subject} materials for personalized AI assistance! 🎓
            """
        
        # General help
        else:
            return """
            🤖 I'm here to help with your studies! While I'm having some connection issues, I can still assist you.<br><br>
            <strong>Try asking about:</strong><br>
            • Study techniques and strategies<br>
            • Memory and retention tips<br>
            • Test preparation methods<br>
            • Time management for studying<br><br>
            Or upload your documents for AI-powered summaries, quizzes, and flashcards! 📚
            """

# Global AI assistant instance
ai_assistant = AIAssistant()

@csrf_exempt
@login_required
def real_time_chat(request):
    """Handle real-time chat requests with enhanced AI responses"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '').strip()
            
            if not question:
                return JsonResponse({
                    'response': "Please ask me a question! I'm here to help with your studies. 📚",
                    'status': 'success'
                })
            
            # Get user context if available
            user_context = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                # Could add user's recent documents or study history as context
                user_context = f"Student: {request.user.username}"
            
            # Generate AI response
            response = ai_assistant.generate_response(question, user_context)
            
            return JsonResponse({
                'response': response,
                'status': 'success',
                'timestamp': json.dumps(str(os.times()))
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'response': 'Invalid request format. Please try again.',
                'status': 'error'
            })
        except Exception as e:
            print(f"Chat error: {e}")
            return JsonResponse({
                'response': ai_assistant.generate_fallback_response(question if 'question' in locals() else 'help'),
                'status': 'error'
            })
    
    return JsonResponse({
        'response': 'Invalid request method. Please use POST.',
        'status': 'error'
    })

@csrf_exempt
def quick_help(request):
    """Provide quick help responses for common study questions"""
    if request.method == 'GET':
        help_topics = {
            'study_tips': {
                'title': 'Study Tips',
                'content': 'Active recall, spaced repetition, and focused practice sessions work best!'
            },
            'memory': {
                'title': 'Memory Techniques', 
                'content': 'Use mnemonics, visual associations, and regular review to boost retention.'
            },
            'time_management': {
                'title': 'Time Management',
                'content': 'Plan your study schedule, take regular breaks, and prioritize important topics.'
            },
            'test_prep': {
                'title': 'Test Preparation',
                'content': 'Practice with mock tests, review weak areas, and start preparation early.'
            }
        }
        
        return JsonResponse({
            'help_topics': help_topics,
            'status': 'success'
        })
    
    return JsonResponse({
        'message': 'Invalid request method.',
        'status': 'error'
    })