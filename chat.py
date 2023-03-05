import openai
import os
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
        print("Say something!")
        audio = r.listen(source)

    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        # convert the audio to text
        print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
        speech = r.recognize_google(audio)
        print("This is what we think was said: " + speech)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    return speech

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
    os.system("mpg321 response.mp3")
    playsound("response.mp3", block=False) # There’s an optional second argument, block, which is set to True by default. Setting it to False makes the function run asynchronously.

def main():
    # run the program
    prompt = recognize_speech()
    print(f"This is the prompt being sent to OpenAI" + prompt)
    responses = chatgpt_response(prompt)
    message = responses.choices[0].text
    print(message)
    generate_audio_file(message)
    play_audio_file()

if __name__ == "__main__":
    main()