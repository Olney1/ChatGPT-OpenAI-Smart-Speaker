# Speech recognition and text-to-speech using OpenAI and gTTS

This script allows you to use speech recognition to input a prompt, send the prompt to OpenAI to generate a response, and then use gTTS to convert the response to an audio file and play the audio file.

## Prerequisites

- You need to have a valid OpenAI API key. You can sign up for a free API key at https://beta.openai.com/.
- You need to install the following packages: `openai`, `gTTS`, `pyaudio`, `SpeechRecognition`, `playsound`. You can install these packages using `pip install openai gTTS pyaudio SpeechRecognition playsound` or use pipenv if you wish to contain a virtual environment.

## Usage

1. Replace `YOUR_API_KEY_HERE` in the following line with your actual OpenAI API key: `openai.api_key = "YOUR_API_KEY_HERE"`
2. Run the script using `python smart_speaker.py`.
3. The script will prompt you to say something. Speak a sentence into your microphone. You may need to allow the program permission to access your microphone on a Mac, a prompt should appear when running the program.
4. The script will send the spoken sentence to OpenAI, generate a response using the text-to-speech model, and play the response as an audio file.

## Customization

- You can change the OpenAI model engine by modifying the value of `model_engine`. For example, to use the "davinci" engine, set `model_engine = "davinci"`.
- You can change the language of the generated audio file by modifying the value of `language`. For example, to generate audio in French, set `language = 'fr'`.
- You can adjust the `temperature` parameter in the following line to control the randomness of the generated response:

```
response = openai.Completion.create(
engine=model_engine,
prompt=prompt,
max_tokens=1024,
n=1,
temperature=0.7,
)
```

Higher values of `temperature` will result in more diverse and random responses, while lower values will result in more deterministic responses.
