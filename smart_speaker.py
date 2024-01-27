import os
from openai import OpenAI
import pyaudio
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from dotenv import load_dotenv
import apa102
import threading
from gpiozero import LED
try:
    import queue as Queue
except ImportError:
    import Queue as Queue
from alexa_led_pattern import AlexaLedPattern
 
# Load the environment variables
load_dotenv()
# Create an OpenAI API client
client = OpenAI()
 
# load pixels Class
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
 
 
# settings and keys
model_engine = "gpt-4-0125-preview"
language = 'en'
 
def recognize_speech():
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Waiting for wake word...")
        while True:
            try:
                r.adjust_for_ambient_noise(source)
                audio_stream = r.listen(source)
                # recognize speech using Google Speech Recognition
                try:
                    # convert the audio to text
                    print("Google Speech Recognition thinks you said " + r.recognize_google(audio_stream))
                    speech = r.recognize_google(audio_stream)
                    if ("Lily" not in speech) and ("lily" not in speech):
                        # the wake word was not detected in the speech
                        print("Wake word not detected in the speech")
   						# Close the current microphone object
                        return False
                    else:
                        # the wake word was detected in the speech
                        print("Found wake word!")
                        # wake up the display
                        pixels.wakeup()
                        return True
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                    print("Waiting for wake word...")
                    return False
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
                    print("Waiting for wake word...")
                    return False
            except KeyboardInterrupt:
                print("Interrupted by User Keyboard")
                break
 
def speech():
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Waiting for user to speak...")
        while True:
            try:
                r.adjust_for_ambient_noise(source)
                audio_stream = r.listen(source)
                # recognize speech using Google Speech Recognition
                try:
                    # convert the audio to text
                    print("Google Speech Recognition thinks you said " + r.recognize_google(audio_stream))
                    speech = r.recognize_google(audio_stream)
                    # wake up thinking LEDs
                    pixels.think()
                    return speech
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                    pixels.off()
                    print("Waiting for user to speak...")
                    continue
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
                    pixels.off()
                    print("Waiting for user to speak...")
                    continue
            except KeyboardInterrupt:
                print("Interrupted by User Keyboard")
                break
            
 
def chatgpt_response(prompt):
    # send the converted audio text to chatgpt
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        temperature=0.7,
    )
    return response
 
def generate_audio_file(text):
    # convert the text response from chatgpt to an audio file 
    audio = gTTS(text=text, lang=language, slow=False)
    # save the audio file
    audio.save("response.mp3")
 
def play_audio_file():
    # play the audio file and wake speaking LEDs
    pixels.speak()
    # os.system("mpg321 response.mp3")
    playsound("response.mp3", block=False) # There’s an optional second argument, block, which is set to True by default. Setting it to False makes the function run asynchronously.
 
def main():
    # run the program
    while True:
        if recognize_speech():
            prompt = speech()
            print(f"This is the prompt being sent to OpenAI: {prompt}")
            responses = chatgpt_response(prompt)
            message = responses.choices[0].text
            print(message)
            generate_audio_file(message)
            play_audio_file()
            pixels.off()
        else:
            print("Speech was not recognised")
            pixels.off()
 
if __name__ == "__main__":
    main()
