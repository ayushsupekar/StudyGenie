from django.urls import path
from . import views

urlpatterns = [
    path('<int:doc_id>/', views.flashcards_view, name='flashcards'),
    path('mark/<int:flashcard_id>/', views.mark_difficulty, name='mark_difficulty'),
]