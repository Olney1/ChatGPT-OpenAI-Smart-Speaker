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

os.chdir('/home/pi/ChatGPT-OpenAI-Smart-Speaker')

pre_prompt = "You are a helpful smart speaker called Jeffers! Please respond with short and concise answers to the following user question and always remind the user at the end to say your name again to continue the conversation:"

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

silence = AudioSegment.silent(duration=1000)

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

pixels = Pixels()

model_engine = "gpt-4-0125-preview"
language = 'en'

def detect_wake_word():
    porcupine = None
    pa = None
    audio_stream = None

    try:
        # Path to the custom wake word .ppn file
        custom_wake_word_path = os.path.join(os.path.dirname(__file__), 'wake_words', 'custom_model/Jeffers.ppn')
        
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
    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()
    return False

def recognise_speech():
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
    if prompt is not None:
        # Add a holding messsage like the one below to deal with current TTS delays until such time that TTS can be streamed due to initial buffering how pydub handles audio in memory
        silence = AudioSegment.silent(duration=1000) 
        holding_audio_response = silence + AudioSegment.from_mp3("sounds/holding.mp3")
        play(holding_audio_response)
        # send the converted audio text to chatgpt
        response = client.chat.completions.create(
            model=model_engine,
            messages=[{"role": "system", "content": pre_prompt},
                      {"role": "user", "content": prompt}],
            max_tokens=400,
            n=1,
            temperature=0.7,
        )
        # Whilst we are waiting for the response, we can play a checking message to improve the user experience.
        checking_on_that = silence + AudioSegment.from_mp3("sounds/checking.mp3")
        play(checking_on_that)
        return response
    else:
        return None
 
def generate_audio_file(message):
    speech_file_path = Path(__file__).parent / "response.mp3"
    response = client.audio.speech.create(
    model="tts-1",
    voice="fable",
    input=message
)
    response.stream_to_file(speech_file_path)
 
def play_wake_up_audio():
    # play the audio file and wake speaking LEDs
    pixels.speak()
    audio_response = silence + AudioSegment.from_mp3("response.mp3")
    play(audio_response)

def main():
    pixels.wakeup()
    device_on = silence + AudioSegment.from_mp3("sounds/on.mp3")
    play(device_on)
    hello = silence + AudioSegment.from_mp3("sounds/hello.mp3")
    play(hello)
    while True:
        if detect_wake_word():
            prompt = recognise_speech()
            if prompt:
                print(f"This is the prompt being sent to OpenAI: {prompt}")
                response = chatgpt_response(prompt)
                if response:
                    message = response.choices[0].message.content
                    print(message)
                    generate_audio_file(message)
                    play_wake_up_audio()
                    pixels.off()
                else:
                    print("No prompt to send to OpenAI")
            else:
                print("Speech was not recognised or there was an error.")
                pixels.off()
        else:
            print("Wake word not detected.")
            pixels.off()

if __name__ == "__main__":
    main()
