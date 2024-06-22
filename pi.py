#!/usr/bin/env python3.9
import os
import subprocess
from openai import OpenAI
import pyaudio
import speech_recognition as sr
from gtts import gTTS
from dotenv import load_dotenv
import apa102
import threading
from gpiozero import LED
try:
    import queue as Queue
except ImportError:
    import Queue as Queue
from alexa_led_pattern import AlexaLedPattern
from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play
import time
import pvporcupine
import struct
from picamera import PiCamera, PiCameraError
import base64
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
# Set the working directory for Pi if you want to run this code via rc.local script so that it is automatically running on Pi startup. Remove this line if you have installed this project in a different directory.
os.chdir('/home/pi/ChatGPT-OpenAI-Smart-Speaker')

# This is our pre-prompt configuration to precede the user's question to enable OpenAI to understand that it's acting as a smart speaker and add any other required information. We will send this in the OpenAI call as part of the system content in messages.
pre_prompt = "You are a helpful smart speaker called Jeffers! Please respond with short and concise answers to the following user question and always remind the user at the end to say your name again to continue the conversation:"

load_dotenv()
client = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

# We add 0.5 second silence globally due to initial buffering how pydub handles audio in memory
silence = AudioSegment.silent(duration=500)

# We set the OpenAI model and language settings here
model_engine = "gpt-4o"
language = 'en'

# Load the Tavily Search tool
tool = TavilySearchResults()

class Pixels:
    PIXELS_N = 12

    def __init__(self, pattern=AlexaLedPattern):
        self.pattern = pattern(show=self.show)
        self.dev = apa102.APA102(num_led=self.PIXELS_N)
        self.power = LED(5)
        self.power.on()
        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        self.last_direction = None

    def wakeup(self, direction=0):
        self.last_direction = direction
        def f():
            self.pattern.wakeup(direction)
 
        self.put(f)
 
    def listen(self):
        if self.last_direction:
            def f():
                self.pattern.wakeup(self.last_direction)
            self.put(f)
        else:
            self.put(self.pattern.listen)
 
    def think(self):
        self.put(self.pattern.think)
 
    def speak(self):
        self.put(self.pattern.speak)
 
    def off(self):
        self.put(self.pattern.off)
 
    def put(self, func):
        self.pattern.stop = True
        self.queue.put(func)
 
    def _run(self):
        while True:
            func = self.queue.get()
            self.pattern.stop = False
            func()
 
    def show(self, data):
        for i in range(self.PIXELS_N):
            self.dev.set_pixel(i, int(data[4*i + 1]), int(data[4*i + 2]), int(data[4*i + 3]))
 
        self.dev.show()

# Instantiate the Pixels class
pixels = Pixels()

# Function to set the system volume which is controlled in the main function
def set_system_volume(percentage):
    subprocess.call(['amixer', 'sset', 'PCM,0', f'{percentage}%'])

# This function is called first to detect the wake word "Jeffers" and then proceed to listen for the user's question.
def detect_wake_word():
    # Here we use the Porcupine wake word detection engine to detect the wake word "Jeffers" and then proceed to listen for the user's question.
    porcupine = None
    pa = None
    audio_stream = None

    try:
        # Path to the custom wake word .ppn file
        custom_wake_word_path = os.path.join(os.path.dirname(__file__), 'wake_words', 'custom_model/Jeffers_Pi.ppn')
        print(f"Wake word file path: {custom_wake_word_path}")
        if not os.path.exists(custom_wake_word_path):
            print(f"Error: Wake word file not found at {custom_wake_word_path}")
        
        # Initialize Porcupine with the custom wake word
        # You will need to obtain an access key from Picovoice to use Porcupine (https://console.picovoice.ai/). You can also create your own custom wake word model using the Picovoice Console.
        try:
            porcupine = pvporcupine.create(access_key=os.environ.get("ACCESS_KEY"), keyword_paths=[custom_wake_word_path])
        except pvporcupine.PorcupineInvalidArgumentError as e:
            print(f"Error creating Porcupine instance: {e}")
            # Handle the error here
        try:
            pa = pyaudio.PyAudio()
            audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=pa.get_default_input_device_info()["index"],
            frames_per_buffer=porcupine.frame_length)
        except:
            print("Error with audio stream setup.")
            error_response = silence + AudioSegment.from_mp3("sounds/audio_issue.mp3")
            play(error_response)

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            result = porcupine.process(pcm)
            if result >= 0:
                print("Wake word detected")
                return True
    except:
        # Deal with any errors that may occur from using the PicoVoice Service (https://console.picovoice.ai/)
        print("Error with wake word detection, Porcupine or the PicoVoice Service.")
        error_response = silence + AudioSegment.from_mp3("sounds/picovoice_issue.mp3")
        play(error_response)

    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()
    return False

def initialize_search_agent():
    llm = ChatOpenAI(model="gpt-4o", temperature=0.9)
    search = TavilySearchResults()
    system_message = SystemMessage(
        content="You are an AI assistant that uses Tavily search to answer questions about weather, news, and recent events."
    )
    agent = initialize_agent(
        [search],
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        agent_kwargs={"system_message": system_message},
    )
    return agent

def recognise_speech():
    # Here we use the Google Speech Recognition engine to convert the user's question into text and then send it to OpenAI for a response.
    r = sr.Recognizer()
    with sr.Microphone() as source:
        start_camera = silence + AudioSegment.from_mp3("sounds/start_camera.mp3")
        take_photo = silence + AudioSegment.from_mp3("sounds/take_photo.mp3")
        camera_shutter = silence + AudioSegment.from_mp3("sounds/camera_shutter.mp3")
        agent_search = silence + AudioSegment.from_mp3("sounds/agent.mp3")
        print("Listening for your question...")
        audio_stream = r.listen(source, timeout=5, phrase_time_limit=10)
        print("Processing your question...")
        try:
            speech_text = r.recognize_google(audio_stream)
            print("Google Speech Recognition thinks you said: " + speech_text)

            if any(keyword in speech_text.lower() for keyword in ["weather", "news", "event", "events"]):
                agent = initialize_search_agent()
                print("Phrase 'weather', 'news', or 'event' detected. Using search agent.")
                play(agent_search)
                response = agent.run(speech_text)
                print("Agent response:", response)
                return speech_text, None
            
            if "on the camera" in speech_text.lower() or "turn on the camera" in speech_text.lower():
                print("Phrase 'on the camera' detected.")
                play(start_camera)
                print("Getting ready to capture an image...")
                play(take_photo)
                try:
                    camera = PiCamera()
                    camera.rotation = 180  # Rotate the camera image by 180 degrees - PLEASE REMOVE THIS LINE IF YOUR CAMERA IS ROTATED DIFFERENTLY
                    camera.resolution = (640, 480)
                    camera.start_preview()
                    time.sleep(2)  # Give the camera time to adjust
                    image_path = "captured_image.jpg"
                    camera.capture(image_path)
                    play(camera_shutter)
                    camera.stop_preview()
                    camera.close()
                    print("Photo captured and saved as captured_image.jpg")
                    return speech_text, image_path
                except PiCameraError:
                    print("Pi camera not detected. Proceeding without capturing an image.")
                    return speech_text, None
            
            return speech_text, None
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
    return None, None

def chatgpt_response(prompt):
    # Here we send the user's question to OpenAI's ChatGPT model and then play the response to the user.
    if prompt is not None:
        try:
            # Add a holding message like the one below to deal with current TTS delays until such time that TTS can be streamed due to initial buffering how pydub handles audio in memory
            silence = AudioSegment.silent(duration=1000)
            holding_audio_response = silence + AudioSegment.from_mp3("sounds/holding.mp3")
            play(holding_audio_response)

            # send the converted audio text to chatgpt
            response = client.chat.completions.create(
                model=model_engine,
                messages=[{"role": "system", "content": pre_prompt}, {"role": "user", "content": prompt}],
                max_tokens=400,
                n=1,
                temperature=0.7,
            )

            # Whilst we are waiting for the response, we can play a checking message to improve the user experience.
            checking_on_that = silence + AudioSegment.from_mp3("sounds/checking.mp3")
            play(checking_on_that)

            return response
        except Exception as e:
            # If there is an error, we can play a message to the user to indicate that there was an issue with the API call.
            print(f"An API error occurred: {str(e)}")
            error_message = silence + AudioSegment.from_mp3("sounds/openai_issue.mp3")
            play(error_message)
            return None
    else:
        return None

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def chatgpt_response_with_image(prompt, image_path):
    if prompt is not None:
        try:
            # Add a holding message like the one below to deal with current TTS delays until such time that TTS can be streamed due to initial buffering how pydub handles audio in memory
            silence = AudioSegment.silent(duration=1000)
            holding_audio_response = silence + AudioSegment.from_mp3("sounds/holding.mp3")
            play(holding_audio_response)
            
            # Encode the image as base64
            base64_image = encode_image(image_path)
            
            # Send the converted audio text and image to ChatGPT
            response = client.chat.completions.create(
                model=model_engine,
                messages=[
                    {"role": "system", "content": pre_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=400,
                n=1,
                temperature=0.7,
            )
            
            # Whilst we are waiting for the response, we can play a checking message to improve the user experience.
            checking_on_that = silence + AudioSegment.from_mp3("sounds/checking.mp3")
            play(checking_on_that)
            
            return response
        except Exception as e:
            # If there is an error, we can play a message to the user to indicate that there was an issue with the API call.
            print(f"An API error occurred: {str(e)}")
            error_message = silence + AudioSegment.from_mp3("sounds/openai_issue.mp3")
            play(error_message)
            return None
    else:
        return None
 
def generate_audio_file(message):
    # This is a standalone function to generate an audio file from the response from OpenAI's ChatGPT model.
    speech_file_path = Path(__file__).parent / "response.mp3"
    response = client.audio.speech.create(
    model="tts-1",
    voice="fable",
    input=message
)
    response.stream_to_file(speech_file_path)
 
def play_response():
    # This is a standalone function to which we can call to play the audio file and wake speaking LEDs to indicate that the smart speaker is responding to the user.
    pixels.speak()
    audio_response = silence + AudioSegment.from_mp3("response.mp3")
    play(audio_response)

def main():
    # Set the system volume
    set_system_volume(90)
    # This is the main function that runs the program.
    pixels.wakeup()
    device_on = silence + AudioSegment.from_mp3("sounds/on.mp3")
    play(device_on)
    hello = silence + AudioSegment.from_mp3("sounds/hello.mp3")
    play(hello)
    pixels.off()
    while True:
        print("Waiting for wake word...")
        if detect_wake_word():
            pixels.listen()  # Indicate that the speaker is listening
            prompt, image_path = recognise_speech()
            if prompt:
                print(f"This is the prompt being sent to OpenAI: {prompt}")
                if image_path:
                    response = chatgpt_response_with_image(prompt, image_path)
                else:
                    response = chatgpt_response(prompt)
                if response:
                    message = response.choices[0].message.content
                    print(message)
                    generate_audio_file(message)
                    play_response()
                    pixels.off()
                else:
                    print("No prompt to send to OpenAI")
                    pixels.off()
            else:
                print("Speech was not recognised or there was an error.")
                pixels.off()
        # After processing (or failure to process), the loop will continue, returning to wake word detection.

if __name__ == "__main__":
    main()