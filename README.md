# ChatGPT Smart Speaker (speech recognition and text-to-speech using OpenAI and Google Speech Recognition)

![Jeff the smart speaker](images/smart_speaker_pi.png)

## Video Demo

[Video Demo using activation word "Jeffers"](videos/demo.mp4)
<br>
<br>

## Equipment List:

## - [Raspberry Pi 4b 4GB](https://www.amazon.co.uk/Raspberry-Pi-Model-4GB/dp/B09TTNF8BT?_encoding=UTF8&tag=olney104-21 "Raspberry Pi 4b 4GB")
## - [VMini External USB Stereo Speaker](https://www.amazon.co.uk/Speakers-Computer-Speaker-Soundbar-Checkout/dp/B08NDJDFPS?_encoding=UTF8&tag=olney104-21 "VMini External USB Stereo Speaker")
## - [VReSpeaker 4-Mic Array](https://www.amazon.co.uk/Seeed-ReSpeaker-4-Mic-Array-Raspberry/dp/B076SSR1W1?&_encoding=UTF8&tag=olney104-21 "VReSpeaker 4-Mic Array")
## - [ANSMANN 10,000mAh Type-C 20W PD Power Bank](https://www.amazon.co.uk/Powerbank-10000mAh-capacity-Smartphones-rechargeable-Black/dp/B01NBNH2AL/?_encoding=UTF8&tag=olney104-21 "ANSMANN 10,000mAh Type-C 20W PD Power Bank")

<br>

## Running on your PC/MAC (use the chat.py or test.py script)

The `chat.py` script allows you to use speech recognition to input a prompt, send the prompt to OpenAI to generate a response, and then use gTTS to convert the response to an audio file and play the audio file on your Mac/PC. Your PC/Mac must have a working default microphone and speakers for this script to work. Please note that this script was designed on a Mac, so additional dependencies may be required on Windows and Linux. 

<br>

## Running on Raspberry Pi (use the smart_speaker.py script)

The `smart_speaker.py` script implements the same functionality on a Raspberry Pi. Please read the important notes in the section below and ensure that you have the `smart_speaker.py` script along with `apa102.py` and `alexa_led_pattern.py` scripts in the same folder together on your Pi if you plan to use the ReSpeaker hardware. You will need to have a microphone attached to your Raspberry Pi otherwise. I am using the in-built microphone on the RESPEAKER and a seperate USB speaker for output. Ensure that these are setup correctly. You can test that the speaker and microphone are set up correctly as the default devices by using a software program such as Audacity. Audacity is buggy on startup but still works on a Raspberry Pi (see instructions in the important notes section below).

<br>

## Prerequisites - chat.py

- You need to have a valid OpenAI API key. You can sign up for a free API key at https://platform.openai.com.
- You'll need to be running Python version 3.7.3 or higher. I am using 3.11.4 on a Mac and 3.7.3 on Raspberry Pi.
- Run `brew install portaudio` after installing HomeBrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- You need to install the following packages: `openai`, `gTTS`, `pyaudio`, `SpeechRecognition`, `playsound, python-dotenv` and `pyobjc` if you are on a Mac. You can install these packages using pip or use pipenv if you wish to contain a virtual environment. 
- Firstly, update your tools: `pip install --upgrade pip setuptools` then `pip install openai pyaudio SpeechRecognition gTTS playsound python-dotenv apa102-pi gpiozero pyobjc`

<br>

## Prerequisites - smart_speaker.py
To run smart_speaker.py you will need a Raspberry Pi 4b (I'm using the 4GB model but 2GB should be enough), ReSpeaker 4-Mic Array for Raspberry Pi and USB speakers.

Run the following on your Raspberry Pi terminal:

1. `sudo apt update`

2. `sudo apt install python3-gpiozero`

3. `git clone https://github.com/Olney1/ChatGPT-OpenAI-Smart-Speaker`

4. You need to install the following packages: `openai`, `gTTS`, `pyaudio`, `SpeechRecognition`, `pydub, python-dotenv`. You can install these packages using pip or use pipenv if you wish to contain a virtual environment. Python 3.11 requires a virtual environment on your Pi.
Firstly, update your tools: `pip install --upgrade pip setuptools` then `pip install openai pyaudio SpeechRecognition gTTS pydub python-dotenv apa102-pi gpiozero`

5. PyAudio relies on PortAudio as a dependency. You can install it using the following command: `sudo apt-get install portaudio19-dev`

6. Pydub dependencies: You need to have ffmpeg installed on your system. On a Raspberry Pi you can install it using: `sudo apt-get install ffmpeg`. You may also need simpleaudio if you run into issues with the script hanging when finding the wake word, so it's best to install these packages just in case: `sudo apt-get install python3-dev` (for development headers to compile) and `install simpleaudio` (for a different backend to play mp3 files) and `sudo apt-get install libasound2-dev` (necessary dependencies).

7. Install support for the lights on the RESPEAKER board. You'll need APA102 LED: `sudo apt install -y python3-rpi.gpio` and then `sudo pip3 install apa102-pi`

8. Activate SPI: sudo raspi-config; Go to "Interface Options"; Go to "SPI"; Enable SPI; While you are at it: Do change the default password! Exit the tool and reboot.

9. Get the Seeed voice card source code, install and reboot: 
`git clone https://github.com/HinTak/seeed-voicecard.git`
`cd seeed-voicecard`
`sudo ./install.sh`
`sudo reboot now`

10. Finally, load audio output on Raspberry Pi `sudo raspi-config`
-Select 1 System options
-Select S2 Audio
-Select your preferred Audio output device
-Select Finish

<br>

## Usage - applies to chat.py:

1. You'll need to set up the environment variable for your Open API Key. To do this create a `.env` file in the same directory and add your API Key to the file like this: `OPENAI_API_KEY="API KEY GOES HERE"`. This is safer than hard coding your API key into the program.
You must not change the name of the variable `OPENAI_API_KEY`.
2. Run the script using `python chat.py`.
3. The script will prompt you to say something. Speak a sentence into your microphone. You may need to allow the program permission to access your microphone on a Mac, a prompt should appear when running the program.
4. The script will send the spoken sentence to OpenAI, generate a response using the text-to-speech model, and play the response as an audio file.

<br>

## Usage - applies to smart_speaker.py:
1. You'll need to set up the environment variable for your Open API Key. To do this create a `.env` file in the same directory and add your API Key to the file like this: `OPENAI_API_KEY="API KEY GOES HERE"`. This is safer than hard coding your API key into the program. You must not change the name of the variable `OPENAI_API_KEY`.
2. Ensure that you have the `smart_speaker.py` script along with `apa102.py` and `alexa_led_pattern.py` scripts in the same folder saved on your Pi if using ReSpeaker.
3. Run the script using `python smart_speaker.py`.
4. The script will prompt you to say the wake word which is programmed into the file `smart_speaker.py` as 'Jeffers'. You can change this to any name you want. Once the wake word has been detected the lights will light up blue. It will now be ready for you to ask your question. When you have asked your question, or when the microphone picks up and processes noise, the lights will rotate a blue colour meaning that your recording sample/question is being sent to OpenAI.
5. The script will then generate a response using the text-to-speech model, and play the response as an audio file.

<br>

## Customisation

- You can change the OpenAI model engine by modifying the value of `model_engine`. For example, to use the "gpt-3.5-turbo" model for a cheaper and quicker response but with a knowledge cut-off to Sep 2021, set `model_engine = "gpt-3.5-turbo"`.
- You can change the language of the generated audio file by modifying the value of `language`. For example, to generate audio in French, set `language = 'fr'`.
- You can adjust the `temperature` parameter in the following line to control the randomness of the generated response:

```
response = client.chat.completions.create(
        model=model_engine,
        messages=[{"role": "system", "content": "You are a helpful smart speaker called Jeffers!"}, # Play about with more context here.
                  {"role": "user", "content": prompt}],
        max_tokens=1024,
        n=1,
        temperature=0.7,
    )
    return response
```

Higher values of `temperature` will result in more diverse and random responses, while lower values will result in more deterministic responses.

<br>

## Important notes for Raspberry Pi Installation

If you are using the same USB speaker in my video you will need to run `sudo apt-get install pulseaudio` to install support for this.

If you want to use ReSpeaker for the lights, you can purchase this from most of the major online stores that stock Raspberry Pi. 
Here is the online guide: https://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/

To test your microphone and speakers install Audacity on your Raspberry Pi:

`sudo apt update`

`sudo apt install audacity`

`audacity`

On the raspberry pi you may encounter an error regarding the installation of `flac`.

See here for the resolution: https://raspberrypi.stackexchange.com/questions/137630/im-unable-to-install-flac-on-my-raspberry-pi-3

The files you will need are going to be here: https://archive.raspbian.org/raspbian/pool/main/f/flac/
<br>Please note the links below may have changed or be updated, so please refer back to this link above for the latest file names and then update your command below.
 
`sudo apt-get install libogg0`

`$ wget https://archive.raspbian.org/raspbian/pool/main/f/flac/libflac8_1.3.2-3+deb10u3_armhf.deb`

`$ wget https://archive.raspbian.org/raspbian/pool/main/f/flac/flac_1.3.2-3+deb10u3_armhf.deb`

`$ sudo dpkg -i libflac8_1.3.2-3+deb10u3_armhf.deb` 

`$ sudo dpkg -i flac_1.3.2-3+deb10u3_armhf.deb`

`$ which flac`
`/usr/bin/flac`

`sudo reboot`

`$ flac --version`
`flac 1.3.2`

You may find you need to install GStreamer if you encounter errors regarding Gst.

Install GStreamer: Open a terminal and run the following command to install GStreamer and its base plugins:

`sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good`
This installs the GStreamer core, along with a set of essential and good-quality plugins.

Next, you need to install the Python bindings for GStreamer. Use this command:

`sudo apt-get install python3-gst-1.0`
This command installs the GStreamer bindings for Python 3.

Install Additional GStreamer Plugins (if needed): Depending on the audio formats you need to work with, you might need additional GStreamer plugins. For example, to install plugins for MP3 playback, use:

`sudo apt-get install gstreamer1.0-plugins-ugly`

To quit a running script on Pi from boot: `ALT + PrtScSysRq (or Print button) + K`

<br>

## Credit to:
https://github.com/tinue/apa102-pi & Seeed Technology Limited for supplementary code.

<br>

## Read more about what is next for the project
https://medium.com/@ben_olney/openai-smart-speaker-with-raspberry-pi-5e284d21a53e