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
            task = process_audio.delay(audio_file_path)
            
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

class ExtractAudioView(APIView):
    def post(self, request):
        video_url = request.data.get('video_url')
        if video_url:
            try:
                # Download the video from the provided URL
                response = requests.get(video_url)
                response.raise_for_status()  # Raise an error for non-200 responses
                video_content = response.content
                
                # Save the downloaded video temporarily
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                video_file_name = os.path.basename(video_url)
                video_file_path = os.path.join(temp_dir, video_file_name)
                with open(video_file_path, 'wb') as f:
                    f.write(video_content)
                
                # Extract audio using ffmpeg
                audio_file_path = os.path.join(temp_dir, os.path.splitext(video_file_name)[0] + '.mp3')
                command = f'ffmpeg -i {video_file_path} -vn -acodec copy {audio_file_path}'
                os.system(command)
                
                # Check if the audio file was created
                if os.path.exists(audio_file_path):
                    # Return the path to the extracted audio file
                    return Response({'audio_file': audio_file_path}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Failed to extract audio'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Please provide a video URL'}, status=status.HTTP_400_BAD_REQUEST)
