import threading
import time

import speech_recognition as sr
import pyttsx4
import datetime
from openai import OpenAI
import elevenlabs
from elevenlabs import play
import os
from dotenv import load_dotenv
from exa_py import Exa

load_dotenv()

gptKey: str = os.getenv("OPENAI_API_KEY")
elevenKey: str = os.getenv("ELEVENLABS_API_KEY")
exaKey: str = os.getenv("EXA_KEY")
client: OpenAI = OpenAI(api_key=gptKey)

# initialize voice components
recognizer: sr.Recognizer = sr.Recognizer()
ttsEngine: pyttsx4.Engine = pyttsx4.init()
elevenlabs.set_api_key(api_key=elevenKey)

# initialize integration components
exa: Exa = Exa(exaKey)


def speakAndPrint(text) -> None:
    # audio = elevenlabs.generate(
    #     text=text, voice="Adam", model="eleven_monolingual_v1", api_key=elevenKey
    # )
    # play(audio)
    print(text)
    ttsEngine.say(text=text)
    ttsEngine.runAndWait()


def wishMe() -> None:
    hour: int = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        greeting = "Good Morning, Rod! How may I help you"

    elif 12 <= hour < 18:
        greeting = "Good afternoon, Sir"

    else:
        greeting = "Good evening, Sir"
    speakAndPrint(greeting)


# the assistant will listen to you, go speech to text.
def listen() -> str:
    print(sr.Microphone.list_working_microphones())
    with sr.Microphone(device_index=1) as source:

        print("Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        print(e)
        print("Unable to Recognize your voice.")
        return "None"

    return query


# submit text to LLM
def textToModel(query: str) -> None:
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a personal assistant, named ELO. ELO stands for Enhanced Logical Operative."},
            {"role": "user", "content": query}
        ]
    )
    reply = summarize(completion.choices[0].message.content)
    speakAndPrint(reply)


def summarize(response: str) -> str:
    if response.__len__() > 300:
        print(response)
        return "My LLM backend response is rather lengthy, I'll put it in your console for reading, sir."
    else:
        return response


def listenForKeywords(query: str) -> bool:
    skipLLM = False
    if query == "stop":
        speakAndPrint("Okay, hope I was able to help!")
        exit()
    elif "thanks elo that is all I needed" in query:
        speakAndPrint("Okay, hope I was able to help!")
        exit()
    elif 'search' in query:
        speakAndPrint("I can run a search query for that if you'd like")
        if confirm():
            speakAndPrint("What would you like me to search?")
            desiredSearch = listen()
            contents = exa.search_and_contents(desiredSearch)
            speakAndPrint("I've come up with a couple of results and displayed them in your console")
            print(contents.results)
            skipLLM = True

    return skipLLM


# confirmation as a function seems intuitive.
def confirm() -> bool:
    confirmationQuery = listen()
    if confirmationQuery == "yes" or "ok" or "sure":
        speakAndPrint("Confirmed")
        return True
    else:
        speakAndPrint("alright.")
        return False


def calibrate() -> int:
    speakAndPrint("Hi. Elo is booting up. Please wait.")
    print("Initializing...")
    microphoneDict = sr.Microphone.list_working_microphones()
    print("A list of mics! %s" % microphoneDict)
    print("A list of mic values! %s" % microphoneDict.values())
    for mic in microphoneDict.values():
        if mic == 'Shure MV7':
            return 1
    else:
        speakAndPrint("Please connect your iphone's mic sir.")
        iphone = microphoneDict.get('Skywalker (2) Microphone')
        time.sleep(5)
        return iphone


def main() -> None:
    startup = calibrate()
    if startup == 0:
        speakAndPrint("Not able to connect to audio source")
        exit()
    wishMe()
    while True:
        query = listen().lower()
        if not listenForKeywords(query):
            textToModel(query)
        else:
            break


if __name__ == "__main__":
    main()
