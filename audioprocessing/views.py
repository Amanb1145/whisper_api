# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import process_audio

class ProcessAudioView(APIView):
    def post(self, request):
        if request.FILES.get('audio'):
            audio_file = request.FILES['audio']
            print(audio_file.temporary_file_path(),"abc")
            task = process_audio.delay(audio_file.temporary_file_path())
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
