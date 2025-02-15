import dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os

dotenv.load_dotenv()

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

audio = client.text_to_speech.convert(
    text="The first move is what sets everything in motion. The quick brown fox jumps over the lazy dog.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
)
play(audio)