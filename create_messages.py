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


def understand_speech_issue():

    message = "Sorry, I didn't quite get that."

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("understand.mp3")


def stop():

    message = "No worries, I'll be here when you need me."

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("stop.mp3")


def hello():

    message = "Welcome, my name is Jeffers, I'm your helpful smart speaker. Just say my name and ask me anything."

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("hello.mp3")

hello()