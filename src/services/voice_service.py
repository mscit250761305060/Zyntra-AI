import os
import asyncio
import logging
import edge_tts

logger = logging.getLogger("zyntra.voice_service")

# Data directory for audio
AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

class VoiceService:
    def __init__(self):
        self.voice = "en-US-AriaNeural"  # Default Microsoft Edge TTS voice
        
    async def synthesize(self, text: str, output_path: str) -> bool:
        """Convert text to speech and save as MP3."""
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            return True
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            return False

voice_service = VoiceService()
