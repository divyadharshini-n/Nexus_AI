from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

import speech_recognition as sr
import os
from dotenv import load_dotenv
import requests
import tempfile
from pydub import AudioSegment
# import ffmpeg  # Temporarily disabled

router = APIRouter()

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = 'gemini-2.5-flash-lite'
GEMINI_URL = f'https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}'

@router.post("/voice-to-text/")
async def voice_to_text(file: UploadFile = File(...)):
    # Save uploaded file to a temp file (keep original extension)
    orig_ext = os.path.splitext(file.filename)[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=orig_ext) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Convert to WAV (PCM) if not already
    wav_path = tmp_path
    if orig_ext != '.wav':
        wav_path = tmp_path + '.wav'
        try:
            audio = AudioSegment.from_file(tmp_path)
            audio.export(wav_path, format='wav')
        except Exception as e:
            os.remove(tmp_path)
            raise HTTPException(status_code=400, detail=f"Failed to convert audio: {e}")

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language='en-IN')
    except sr.UnknownValueError:
        os.remove(tmp_path)
        if wav_path != tmp_path:
            os.remove(wav_path)
        raise HTTPException(status_code=400, detail="Could not understand audio.")
    except Exception as e:
        os.remove(tmp_path)
        if wav_path != tmp_path:
            os.remove(wav_path)
        raise HTTPException(status_code=500, detail=f"Failed to process audio: {e}")
    os.remove(tmp_path)
    if wav_path != tmp_path:
        os.remove(wav_path)
    return JSONResponse(content={"text": text})
