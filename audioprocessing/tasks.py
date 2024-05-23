# tasks.py
from celery import shared_task, current_app
# import whisper
import whisper_timestamped as whisper
import os
import uuid
from django.conf import settings
import json

# Create a Celery instance
app = current_app

# Define a Celery task to process audio files
@shared_task(bind=True)
def process_audio(self, audio_file_path):
    try:
        # Load the pre-trained model
        # model = whisper.load_model("base")
        model = whisper.load_model("tiny", device="cpu")
        
        # Load and preprocess the audio file
        audio = whisper.load_audio(audio_file_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        
        # Detect the spoken language
        _, probs = model.detect_language(mel)
        language = max(probs, key=probs.get)
        
        # Decode the audio
        # options = whisper.DecodingOptions()
        # result = whisper.decode(model, mel, options)

        result = whisper.transcribe(model, audio, language=language)

        # Remove the saved audio file
        os.remove(audio_file_path)
        
        # Prepare the response data
        response_data = {
            'language': language,
            'text': result  # Leave the result as a dictionary for now
        }
                    
        # Return the language and recognized text
        return {
            'language': language,
            'text': response_data
        }
    except Exception as e:
        # Handle exceptions gracefully
        return {
            'error': str(e)
        }

# Define a Celery task to fetch the status of a task ID
@shared_task(bind=True)
def get_task_status(self, task_id):
    try:
        task = app.AsyncResult(task_id)
        return {
            'status': task.status,
            'result': task.result
        }
    except Exception as e:
        return {
            'error': str(e)
        }


# @shared_task
# def extract_audio(video_file_path):
#     try:
#         # Generate a unique identifier for the audio file
#         audio_file_uuid = str(uuid.uuid4())
#         audio_file_name = f'{audio_file_uuid}.mp3'
#         audio_file_path = os.path.join(settings.MEDIA_ROOT, 'temp', audio_file_name)
        
#         # Extract audio using ffmpeg
#         command = f'ffmpeg -i {video_file_path} -q:a 0 -map a {audio_file_path}'
#         os.system(command)
        
#         # Check if the audio file was created
#         if os.path.exists(audio_file_path):
#             # Construct the URL for the extracted audio file
#             audio_file_url = os.path.join(settings.MEDIA_URL, 'temp', audio_file_name)
#             # Replace 'http' with 'https'
#             audio_file_url = audio_file_url.replace('http://', 'https://')
#             return {'audio_file_url': "https://service.ai.video.wiki/" + audio_file_url}
#         else:
#             return {'error': 'Failed to extract audio'}
#     except Exception as e:
#         return {'error': str(e)}

@shared_task
def extract_audio(video_file_path):
    try:
        # Generate a unique identifier for the audio file
        audio_file_uuid = str(uuid.uuid4())
        audio_file_name = f'{audio_file_uuid}.mp3'
        audio_file_path = os.path.join(settings.MEDIA_ROOT, 'temp', audio_file_name)

        # Extract audio using ffmpeg
        command = f'ffmpeg -i "{video_file_path}" -q:a 0 -map a "{audio_file_path}"'
        os.system(command)

        # Check if the audio file was created
        if os.path.exists(audio_file_path):
            # Construct the URL for the extracted audio file
            audio_file_url = os.path.join(settings.MEDIA_URL, 'temp', audio_file_name)

            # Replace 'http' with 'https'
            audio_file_url = audio_file_url.replace('http://', 'https://')

            return {'audio_file_url': "https://service.ai.video.wiki/" + audio_file_url}
        else:
            return {'error': 'Failed to extract audio'}

    except Exception as e:
        return {'error': str(e)}
