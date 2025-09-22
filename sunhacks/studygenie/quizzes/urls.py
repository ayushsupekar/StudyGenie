from django.urls import path
from . import views

urlpatterns = [
    path('<int:doc_id>/', views.quiz_view, name='quiz'),
    path('submit/<int:quiz_id>/', views.submit_quiz, name='submit_quiz'),
]