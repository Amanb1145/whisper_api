# views.py
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import process_audio, extract_audio
from django.conf import settings
import requests
import uuid
import urllib.parse


class ProcessAudioView(APIView):
    def post(self, request):
        if request.FILES.get('audio'):
            # If audio file is uploaded
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
        elif 'audio_url' in request.data:
            # If audio URL is provided
            audio_url = request.data['audio_url']
            
            try:
                # Download the audio from the provided URL
                response = requests.get(audio_url)
                response.raise_for_status()  # Raise an error for non-200 responses
                audio_content = response.content
                
                # Save the downloaded audio temporarily
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                audio_file_name = os.path.basename(audio_url)
                audio_file_path = os.path.join(temp_dir, audio_file_name)
                with open(audio_file_path, 'wb') as f:
                    f.write(audio_content)
                
                # Call Celery task to process the audio file asynchronously
                task = process_audio.delay(audio_file_path)
                
                return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Please provide an audio file or audio URL.'}, status=status.HTTP_400_BAD_REQUEST)

class TaskStatusView(APIView):
    def get(self, request, task_id):
        task = process_audio.AsyncResult(task_id)
        if task.state == 'SUCCESS':
            result = task.get()
            return Response(result)
        else:
            return Response({'status': task.state})

# class ExtractAudioView(APIView):
#     def post(self, request):
#         video_url = request.data.get('video_url')
#         if video_url:
#             try:
#                 # Download the video from the provided URL
#                 response = requests.get(video_url)
#                 response.raise_for_status()  # Raise an error for non-200 responses
#                 video_content = response.content
                
#                 # Save the downloaded video temporarily
#                 temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
#                 if not os.path.exists(temp_dir):
#                     os.makedirs(temp_dir)
#                 video_file_name = os.path.basename(video_url)
#                 video_file_path = os.path.join(temp_dir, video_file_name)
#                 with open(video_file_path, 'wb') as f:
#                     f.write(video_content)
                
#                 # Call Celery task to extract audio asynchronously
#                 task = extract_audio.delay(video_file_path)
                
#                 return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
#             except Exception as e:
#                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({'error': 'Please provide a video URL'}, status=status.HTTP_400_BAD_REQUEST)

class ExtractAudioView(APIView):
    def post(self, request):
        video_url = request.data.get('video_url')
        if video_url:
            try:
                # Decode URL to handle special characters
                video_url = urllib.parse.unquote(video_url)
                
                # Set headers including User-Agent
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }
                
                # Download the video from the provided URL
                response = requests.get(video_url, headers=headers)
                response.raise_for_status()  # Raise an error for non-200 responses
                video_content = response.content
                
                # Save the downloaded video temporarily
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                # Extract filename from URL
                url_path = urllib.parse.urlparse(video_url).path
                video_file_name = os.path.basename(url_path) or f'video_{uuid.uuid4()}.mp4'
                video_file_path = os.path.join(temp_dir, video_file_name)
                
                with open(video_file_path, 'wb') as f:
                    f.write(video_content)
                
                # Call Celery task to extract audio asynchronously
                task = extract_audio.delay(video_file_path)
                
                return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
            except requests.exceptions.RequestException as e:
                return Response({'error': f'Request error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Please provide a video URL'}, status=status.HTTP_400_BAD_REQUEST)


class ExtractTaskStatusView(APIView):
    def get(self, request, task_id):
        task = extract_audio.AsyncResult(task_id)
        if task.state == 'SUCCESS':
            result = task.get()
            return Response(result)
        else:
            return Response({'status': task.state})
