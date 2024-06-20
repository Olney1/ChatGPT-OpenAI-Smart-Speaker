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

    response.stream_to_file("sounds/holding.mp3")



def create_google_speech_issue():

    message = "Sorry, there was an issue reaching Google Speech Recognition, please try again."

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("sounds/google_issue.mp3")


def understand_speech_issue():

    message = "Sorry, I didn't quite get that."

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("sounds/understand.mp3")


def stop():

    message = "No worries, I'll be here when you need me."

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("sounds/stop.mp3")


def hello():

    message = "Welcome, my name is Jeffers, I'm your helpful smart speaker. Just say my name and ask me anything."

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("sounds/hello.mp3")


def create_picovoice_issue():

    message = "Sorry, there was an issue with the PicoVoice Service."

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("sounds/picovoice_issue.mp3")


def create_picture_message():

    message = "Let me take a look through the camera."

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("sounds/start_camera.mp3")


def start_picture_message():

    message = "Hold steady....... I'm taking a photo now...... in ....... 3 ...... 2 ......... 1"

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("sounds/take_photo.mp3")


def agent_search():

    message = "Let me do a quick search for you."

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=message,
    )

    response.stream_to_file("sounds/agent.mp3")

agent_search()