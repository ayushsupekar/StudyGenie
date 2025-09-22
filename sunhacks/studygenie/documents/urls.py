from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_document, name='upload_document'),
    path('<int:doc_id>/summary/', views.summary_view, name='summary'),
    path('tutor/<int:doc_id>/', views.tutor_view, name='tutor'),
    path('chatbot/', views.chatbot_api, name='chatbot_api'),
    path('<int:doc_id>/multilang/', views.generate_multilang_content, name='generate_multilang'),
    path('<int:doc_id>/translate/', views.translate_summary, name='translate_summary'),
    path('<int:doc_id>/quiz-lang/', views.get_quiz_in_language, name='quiz_in_language'),
    path('<int:doc_id>/flashcards-lang/', views.get_flashcards_in_language, name='flashcards_in_language'),
]