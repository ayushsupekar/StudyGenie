from django.urls import path
from . import views
from . import ai_assistant

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('ai-chat/', ai_assistant.real_time_chat, name='ai_chat'),
    path('quick-help/', ai_assistant.quick_help, name='quick_help'),
]