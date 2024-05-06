# tasks.py
from celery import shared_task, current_app
import whisper
import os

# Create a Celery instance
app = current_app

# Define a Celery task to process audio files
@shared_task(bind=True)
def process_audio(self, audio_file_path):
    try:
        # Load the pre-trained model
        model = whisper.load_model("base")
        
        # Load and preprocess the audio file
        audio = whisper.load_audio(audio_file_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        
        # Detect the spoken language
        _, probs = model.detect_language(mel)
        language = max(probs, key=probs.get)
        
        # Decode the audio
        options = whisper.DecodingOptions()
        result = whisper.decode(model, mel, options)

        # Remove the saved audio file
        os.remove(audio_file_path)
                    
        # Return the language and recognized text
        return {
            'language': language,
            'text': result.text
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
