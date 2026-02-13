import speech_recognition as sr
from pathlib import Path
from typing import Dict


class VoiceProcessor:
    """Process voice files to text"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def process_audio(self, file_path: str) -> Dict:
        """
        Convert audio file to text
        
        Supports: WAV, MP3 (converted to WAV)
        """
        try:
            path = Path(file_path)
            
            # Load audio file
            with sr.AudioFile(file_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record audio
                audio_data = self.recognizer.record(source)
                
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio_data)
                
                return {
                    "success": True,
                    "text": text,
                    "filename": path.name,
                    "word_count": len(text.split())
                }
        except sr.UnknownValueError:
            return {
                "success": False,
                "error": "Could not understand audio"
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "error": f"Speech recognition service error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process audio: {str(e)}"
            }


# Global instance
voice_processor = VoiceProcessor()