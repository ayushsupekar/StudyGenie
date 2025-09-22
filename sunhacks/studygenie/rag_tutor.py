"""
RAG-based AI Tutor for StudyGenie
Retrieval-Augmented Generation tutor that uses document content for context-aware responses
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from documents.models import Document

# Load environment variables
load_dotenv()

class RAGTutor:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_AI_API_KEY')
        self.model = None
        self.initialize_ai()
    
    def initialize_ai(self):
        """Initialize AI model with API key from .env"""
        try:
            if not self.api_key:
                print("ERROR: GOOGLE_AI_API_KEY not found in .env file")
                return False
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print(f"RAG Tutor initialized with API key: {self.api_key[:10]}...")
            return True
        except Exception as e:
            print(f"RAG Tutor initialization error: {e}")
            return False
    
    def retrieve_relevant_content(self, question, document):
        """Retrieve relevant content from document based on question"""
        if not document.extracted_text:
            return "No document content available."
        
        # Split document into chunks
        text = document.extracted_text
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        # Simple keyword matching for retrieval
        question_words = set(question.lower().split())
        relevant_chunks = []
        
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            # Calculate overlap
            overlap = len(question_words.intersection(sentence_words))
            if overlap > 0:
                relevant_chunks.append((sentence, overlap))
        
        # Sort by relevance and return top chunks
        relevant_chunks.sort(key=lambda x: x[1], reverse=True)
        return ' '.join([chunk[0] for chunk in relevant_chunks[:5]])
    
    def generate_rag_response(self, question, document):
        """Generate response using RAG approach"""
        if not self.model:
            return self.generate_fallback_response(question, document)
        
        try:
            # Retrieve relevant content
            relevant_content = self.retrieve_relevant_content(question, document)
            
            # Create RAG prompt
            rag_prompt = f"""
            You are an AI tutor helping a student understand their study material.
            
            DOCUMENT: {document.title}
            RELEVANT CONTENT: {relevant_content[:2000]}
            STUDENT QUESTION: {question}
            
            Instructions:
            1. Answer ONLY based on the provided document content
            2. If the question is not related to the document, say so politely
            3. Provide clear, educational explanations
            4. Use examples from the document when possible
            5. Keep response under 200 words
            6. Be encouraging and supportive
            
            Response:
            """
            
            response = self.model.generate_content(rag_prompt)
            return self.format_response(response.text.strip(), document.title)
            
        except Exception as e:
            print(f"RAG response error: {e}")
            return self.generate_fallback_response(question, document)
    
    def format_response(self, response, doc_title):
        """Format AI response for display"""
        formatted = response.replace('\n\n', '<br><br>').replace('\n', '<br>')
        formatted += f"<br><br><small class='text-muted'><i class='fas fa-book'></i> Based on: {doc_title}</small>"
        return formatted
    
    def generate_fallback_response(self, question, document):
        """Generate intelligent fallback when AI is unavailable"""
        question_lower = question.lower()
        
        # Try to find relevant content manually
        if document.extracted_text:
            relevant_content = self.retrieve_relevant_content(question, document)
            
            if relevant_content and len(relevant_content) > 50:
                return f"""
                <strong>From your document '{document.title}':</strong><br><br>
                {relevant_content[:300]}...<br><br>
                <small class='text-muted'>This content seems relevant to your question. 
                For more detailed explanations, try rephrasing your question or ask about specific concepts.</small>
                """
        
        # Generic helpful responses
        if any(word in question_lower for word in ['what', 'define', 'explain']):
            return f"""
            <strong>About '{document.title}':</strong><br><br>
            I can help explain concepts from your uploaded document. Try asking more specific questions like:<br>
            • "What is [specific term] mentioned in the document?"<br>
            • "Explain the concept of [topic]"<br>
            • "How does [process] work according to the document?"<br><br>
            <small class='text-muted'>Upload more documents or ask specific questions for better assistance!</small>
            """
        
        elif any(word in question_lower for word in ['how', 'process', 'method']):
            return f"""
            <strong>Process/Method Questions:</strong><br><br>
            Based on '{document.title}', I can help explain processes and methods. Try asking:<br>
            • "How is [specific process] performed?"<br>
            • "What are the steps for [procedure]?"<br>
            • "Explain the method of [technique]"<br><br>
            <small class='text-muted'>Be specific about what process you want to understand!</small>
            """
        
        elif any(word in question_lower for word in ['example', 'examples']):
            return f"""
            <strong>Looking for Examples:</strong><br><br>
            From '{document.title}', I can provide examples when available. Try:<br>
            • "Give me an example of [concept]"<br>
            • "Show examples of [topic] from the document"<br>
            • "What are some practical applications?"<br><br>
            <small class='text-muted'>Ask about specific concepts for targeted examples!</small>
            """
        
        else:
            return f"""
            <strong>AI Tutor for '{document.title}'</strong><br><br>
            I'm here to help you understand your study material! You can ask me:<br>
            • Questions about specific concepts in the document<br>
            • Explanations of terms and definitions<br>
            • How processes or methods work<br>
            • Examples and applications<br><br>
            <small class='text-muted'>Try asking: "What is the main topic?" or "Explain [specific concept]"</small>
            """

# Global RAG tutor instance
rag_tutor = RAGTutor()

@csrf_exempt
def rag_tutor_chat(request, doc_id):
    """Handle RAG-based tutor chat for specific document"""
    if request.method == 'POST':
        try:
            # Get document
            document = Document.objects.get(id=doc_id)
            
            # Parse request
            data = json.loads(request.body)
            question = data.get('question', '').strip()
            
            if not question:
                return JsonResponse({
                    'response': f"Please ask me a question about '{document.title}'! 📚",
                    'status': 'success'
                })
            
            # Generate RAG response
            response = rag_tutor.generate_rag_response(question, document)
            
            return JsonResponse({
                'response': response,
                'status': 'success',
                'document': document.title
            })
            
        except Document.DoesNotExist:
            return JsonResponse({
                'response': 'Document not found. Please select a valid document.',
                'status': 'error'
            })
        except Exception as e:
            print(f"RAG tutor error: {e}")
            return JsonResponse({
                'response': 'Sorry, I encountered an error. Please try again.',
                'status': 'error'
            })
    
    return JsonResponse({
        'response': 'Invalid request method.',
        'status': 'error'
    })