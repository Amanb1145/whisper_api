# tasks.py
from celery import Celery
import whisper

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def process_audio(audio_file_path):
    model = whisper.load_model("base")
    audio = whisper.load_audio(audio_file_path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)
    language = max(probs, key=probs.get)
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)
    return {
        'language': language,
        'text': result.text
    }
