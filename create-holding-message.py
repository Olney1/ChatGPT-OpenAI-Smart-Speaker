from openai import OpenAI
import os
from dotenv import load_dotenv

"""Create your own holding message by running this script with a new message in the input below"""

# Load the environment variables
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

response = client.audio.speech.create(
    model="tts-1",
    voice="fable",
    input="One moment please",
)

response.stream_to_file("holding.mp3")