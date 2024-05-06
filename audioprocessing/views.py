# views.py
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import process_audio
from django.conf import settings

class ProcessAudioView(APIView):
    def post(self, request):
        if request.FILES.get('audio'):
            audio_file = request.FILES['audio']
            
            # Save the uploaded file temporarily
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            audio_file_path = os.path.join(temp_dir, audio_file.name)
            with open(audio_file_path, 'wb') as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)
            
            # Call Celery task to process the audio file asynchronously
            task = process_audio_file.delay(audio_file_path)
            
            return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'error': 'Please provide an audio file.'}, status=status.HTTP_400_BAD_REQUEST)

class TaskStatusView(APIView):
    def get(self, request, task_id):
        task = process_audio.AsyncResult(task_id)
        if task.state == 'SUCCESS':
            result = task.get()
            return Response(result)
        else:
            return Response({'status': task.state})
