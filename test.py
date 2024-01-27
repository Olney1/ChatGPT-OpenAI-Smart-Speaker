import os
from openai import OpenAI
import pyaudio
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from dotenv import load_dotenv
from pathlib import Path

# Load the environment variables
load_dotenv()
# Create an OpenAI API client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# settings and keys
model_engine = "gpt-4-0125-preview"
language = 'en'

def recognize_speech():
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print("Listening...")
            audio_stream = r.listen(source)
            print("Waiting for wake word...")
            # recognize speech using Google Speech Recognition
            try:
                # convert the audio to text
                print("Google Speech Recognition thinks you said " + r.recognize_google(audio_stream))
                speech = r.recognize_google(audio_stream)
                print("Recognized Speech:", speech)  # Print the recognized speech for debugging
                words = speech.lower().split()  # Split the speech into words
                if "jeffers" not in words:
                    print("Wake word not detected in the speech")
                    return False
                else:
                    print("Found wake word!")
                    # pixels.wakeup()
                    # Wake up the display
                    return True
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except KeyboardInterrupt:
            print("Interrupted by User Keyboard")
            pass

def speech():
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Activated! Waiting for your question...")
        try:
            audio_stream = r.listen(source)
            # recognize speech using Google Speech Recognition
            # recognize speech using Google Speech Recognition
            try:
                # convert the audio to text
                print("Google Speech Recognition thinks you said " + r.recognize_google(audio_stream))
                speech = r.recognize_google(audio_stream)
                #pixels.think()
                return speech
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except KeyboardInterrupt:
            print("Interrupted by User Keyboard")
            pass
    return ""
 
def chatgpt_response(prompt):
    # send the converted audio text to chatgpt
    response = client.chat.completions.create(
        model=model_engine,
        messages=[{"role": "system", "content": "You are a helpful smart speaker called Jeffers!"},
                  {"role": "user", "content": prompt}],
        max_tokens=1024,
        n=1,
        temperature=0.7,
    )
    return response
 
def generate_audio_file(message):
    speech_file_path = Path(__file__).parent / "response.mp3"
    response = client.audio.speech.create(
    model="tts-1",
    voice="fable",
    input=message
)
    response.stream_to_file(speech_file_path)
 
def play_audio_file():
    # play the audio file
    # os.system("mpg321 response.mp3")
    playsound("response.mp3", block=False) # There’s an optional second argument, block, which is set to True by default. Setting it to False makes the function run asynchronously.

def main():
    # run the program
    while True:
        if recognize_speech():
            prompt = speech()
            print(f"This is the prompt being sent to OpenAI: {prompt}")
            responses = chatgpt_response(prompt)
            message = responses.choices[0].message.content
            print(message)
            generate_audio_file(message)
            play_audio_file()
        else:
            print("Wake word not detected. Listening again...")
            continue

if __name__ == "__main__":
    main()
