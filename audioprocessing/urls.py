# audioprocessing/urls.py
from django.urls import path
from .views import ProcessAudioView, TaskStatusView, ExtractAudioView, ExtractTaskStatusView

urlpatterns = [
    path('process-audio/', ProcessAudioView.as_view(), name='process_audio'),
    path('task-status/<str:task_id>/', TaskStatusView.as_view(), name='task_status'),
    path('extract-audio/', ExtractAudioView.as_view(), name='extract_audio'),
    path('extract-task-status/<str:task_id>/', ExtractTaskStatusView.as_view(), name='task_status'),
]
