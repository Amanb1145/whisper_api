# audioprocessing/urls.py
from django.urls import path
from .views import ProcessAudioView, TaskStatusView, ExtractAudioView

urlpatterns = [
    path('process-audio/', ProcessAudioView.as_view(), name='process_audio'),
    path('task-status/<str:task_id>/', TaskStatusView.as_view(), name='task_status'),
    path('extract-audio/', ExtractAudioView.as_view(), name='extract_audio'),
]
