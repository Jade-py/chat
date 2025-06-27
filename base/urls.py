from django.urls import path
from .views import chat_view

urlpatterns = [
    path('', chat_view, name='chat'),
    path('<int:dept_id>/', chat_view, name='chat_with_dept'),
]
