import os
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

# Set the working directory for Pi if you want to run this code via rc.local script so that it is automatically running on Pi startup. Remove this line if you have installed this project in a different directory.
os.chdir('/home/pi/ChatGPT-OpenAI-Smart-Speaker')

# This is our pre-prompt configuration to precede the user's question to enable OpenAI to understand that it's acting as a smart speaker and add any other required information. We will send this in the OpenAI call as part of the system content in messages.
pre_prompt = "You are a helpful smart speaker called Jeffers! Please respond with short and concise answers to the following user question and always remind the user at the end to say your name again to continue the conversation:"

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# We add 0.5 second silence globally due to initial buffering how pydub handles audio in memory
silence = AudioSegment.silent(duration=500)

# We set the OpenAI model and language settings here
model_engine = "gpt-4-0125-preview"
language = 'en'

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

def detect_wake_word():
    # Here we use the Porcupine wake word detection engine to detect the wake word "Jeffers" and then proceed to listen for the user's question.
    porcupine = None
    pa = None
    audio_stream = None

    try:
        # Path to the custom wake word .ppn file
        custom_wake_word_path = os.path.join(os.path.dirname(__file__), 'wake_words', 'custom_model/Jeffers_Pi.ppn')
        
        # Initialize Porcupine with the custom wake word
        porcupine = pvporcupine.create(access_key=os.environ.get("ACCESS_KEY"), keyword_paths=[custom_wake_word_path]) # You will need to obtain an access key from Picovoice to use Porcupine (https://console.picovoice.ai/). You can also create your own custom wake word model using the Picovoice Console.
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length)

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

def recognise_speech():
    # Here we use the Google Speech Recognition engine to convert the user's question into text and then send it to OpenAI for a response.
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your question...")
        audio_stream = r.listen(source, timeout=5, phrase_time_limit=10)
        print("Processing your question...")
        try:
            speech_text = r.recognize_google(audio_stream)
            print("Google Speech Recognition thinks you said: " + speech_text)
            return speech_text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
    return None

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
            prompt = recognise_speech()
            if prompt:
                print(f"This is the prompt being sent to OpenAI: {prompt}")
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
