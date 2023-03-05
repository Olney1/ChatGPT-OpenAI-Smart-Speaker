import os
import openai
import pyaudio
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# settings and keys
openai.api_key = os.environ.get('OPENAI_API_KEY')
model_engine = "text-davinci-003"
language = 'en'

def recognize_speech():
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Waiting for wake word...")
        try:
            audio_stream = r.listen(source)
            # recognize speech using Google Speech Recognition
            try:
                # convert the audio to text
                print("Google Speech Recognition thinks you said " + r.recognize_google(audio_stream))
                speech = r.recognize_google(audio_stream)
                if ("Jeffers" not in speech) and ("jeffers" not in speech):
                    # the wake word was not detected in the speech
                    print("Wake word not detected in the speech")
                    return False
                else:
                    # the wake word was detected in the speech
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
        print("Waiting for user to speak...")
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
    # play the audio file
    # os.system("mpg321 response.mp3")
    playsound("response.mp3", block=False) # There’s an optional second argument, block, which is set to True by default. Setting it to False makes the function run asynchronously.

def main():
    # run the program
    while True:
        recognize_speech()
        if recognize_speech():
            prompt = speech()
            print(f"This is the prompt being sent to OpenAI: {prompt}")
            responses = chatgpt_response(prompt)
            message = responses.choices[0].text
            print(message)
            generate_audio_file(message)
            play_audio_file()
        else:
            print("Speech was not recognised")
            continue

if __name__ == "__main__":
    main()
