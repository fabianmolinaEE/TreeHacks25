from openai import OpenAI
import dotenv
import os

dotenv.load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Testing with a sample audio file.
audio_file= open("harvard.wav", "rb")
transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
)

print(transcription.text)