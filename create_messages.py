from openai import OpenAI
import os
from dotenv import load_dotenv

"""Create your own professional messages with OpenAI for your speaker"""

# Load the environment variables
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def create_holding_message():

    message = "One moment please"

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("holding.mp3")



def create_google_speech_issue():

    message = "Sorry, there was an issue reaching Google Speech Recognition, please try again."

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("google_issue.mp3")


create_google_speech_issue()