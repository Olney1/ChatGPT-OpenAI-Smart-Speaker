from openai import OpenAI
import os
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
model_engine = "gpt-4o"
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
        print("Google Speech Recognition thinks you said: " + r.recognize_google(audio))
        speech = r.recognize_google(audio)
        print("This is what we think was said: " + speech)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    # Add a holding messsage like the one below to deal with current TTS delays until such time that TTS can be streamed.
    playsound("sounds/holding.mp3") # There’s an optional second argument, block, which is set to True by default. Setting it to False makes the function run asynchronously.

    return speech

def chatgpt_response(prompt):
    # send the converted audio text to chatgpt
    response = client.chat.completions.create(
        model=model_engine,
        messages=[{"role": "system", "content": "You are a helpful smart speaker called Jeffers!"},
                  {"role": "user", "content": prompt}],
        max_tokens=300,
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
    playsound("response.mp3") # There’s an optional second argument, block, which is set to True by default. Setting it to False makes the function run asynchronously.

def main():
    # run the program
    prompt = recognize_speech()
    print(f"This is the prompt being sent to OpenAI: " + prompt)
    responses = chatgpt_response(prompt)
    message = responses.choices[0].message.content
    print(message)
    generate_audio_file(message)
    play_audio_file()

if __name__ == "__main__":
    main()