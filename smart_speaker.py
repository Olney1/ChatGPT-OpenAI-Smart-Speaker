import openai
import os
import pyaudio
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound

openai.api_key = "YOUR_API_KEY_HERE"
model_engine = "text-davinci-002"
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
        print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
        speech = r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    return speech

def get_completions(prompt):
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        temperature=0.7,
    )
    return completions

def generate_audio_file(text):
    myobj = gTTS(text=text, lang=language, slow=False)
    myobj.save("response.mp3")

def play_audio_file():
    os.system("mpg321 response.mp3")
    playsound("response.mp3", block=False) # There’s an optional second argument, block, which is set to True by default. Setting it to False makes the function run asynchronously.

def main():
    prompt = recognize_speech()
    print(f"This is the prompt being sent to OpenAI" + prompt)
    completions = get_completions(prompt)
    message = completions.choices[0].text
    print(message)
    generate_audio_file(message)
    play_audio_file()

if __name__ == "__main__":
    main()
