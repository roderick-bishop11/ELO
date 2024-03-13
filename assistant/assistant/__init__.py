import time
import datetime
import os
import logging
import speech_recognition as sr
import pyttsx4
from openai import OpenAI
import elevenlabs
from elevenlabs import play
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

# Create and configure logger
today = datetime.datetime.now().__str__()
logging.basicConfig(filename=f"log{today}.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 
logger = logging.getLogger()

# todo: timer metrics on request completion time
# todo: GPT-4


def speak_and_print(text) -> None:
    audio = elevenlabs.generate(
        text=text, voice="George", model="eleven_monolingual_v1", api_key=elevenKey
    )
    play(audio)
    print(text)
    # ttsEngine.say(text=text)
    # ttsEngine.runAndWait()


def wish_me() -> None:
    hour: int = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        greeting = "Good Morning, Rod! How may I help you"

    elif 12 <= hour < 18:
        greeting = "Good afternoon, Sir"

    else:
        greeting = "Good evening, Sir"
    speak_and_print(greeting)


# the assistant will listen to you, go speech to text.
def listen() -> str:
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
def text_to_model(query: str) -> None:
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a personal assistant, named ELO. ELO stands for Enhanced Logical Operative."},
            {"role": "user", "content": query}
        ]
    )
    reply = summarize(completion.choices[0].message.content)
    speak_and_print(reply)


def summarize(response: str) -> str:
    if response.__len__() > 300:
        print(response)
        return "My LLM backend response is rather lengthy, I'll put it in your console for reading, sir."
    else:
        return response


def parse_keywords(query: str) -> bool:
    skipLLM = False
    if query == "stop":
        speak_and_print("Okay, hope I was able to help!")
        os._exit(0)
    elif "thanks elo that is all I needed" in query:
        speak_and_print("Okay, hope I was able to help!")
        os._exit(0)
    elif 'search' in query:
        speak_and_print("I can run a search query for you. Please confirm")
        if confirm():
            speak_and_print("What would you like me to search?")
            desiredSearch = listen()
            contents = exa.search_and_contents(desiredSearch)
            speak_and_print("I've come up with a couple of results and displayed them in your console")
            print(contents.results)
            skipLLM = True

    return skipLLM


# confirmation as a function seems intuitive.
def confirm() -> bool:
    confirmationQuery = listen()
    if confirmationQuery == "yes" or "ok" or "sure":
        speak_and_print("Confirmed")
        return True
    else:
        speak_and_print("alright.")
        return False

#todo: calibrate function needs to also set a mic to use for the session. This way it makes it smoother. 
def calibrate() -> int:
    speak_and_print("Hi. Elo is booting up. Please wait.")
    print("Initializing...")
    microphones = sr.Microphone.list_working_microphones()
    print("A list of mics! %s" % microphones)
    print("A list of mic values! %s" % microphones.values())
    for mic in microphones.values():
        if mic == 'Shure MV7':
            return 1
        logger.info(f"ELO Chose device 1{microphones.get('Shure MV7')}")
    else:
        speak_and_print("Please connect your iphone's mic sir.")
        iphone = microphones.get('Skywalker (2) Microphone')
        time.sleep(5)
        return iphone


def main() -> None:
    startup = calibrate()
    if startup == 0:
        speak_and_print("Not able to connect to audio source")
        quit(0) 
    wish_me
    while True:
        query = listen().lower()
        if not parse_keywords(query):
            text_to_model(query)
        else:
            pass


if __name__ == "__main__":
    main()
