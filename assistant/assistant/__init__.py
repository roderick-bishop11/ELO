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
import pygame
import math
import pyaudio
from icecream import ic
import threading

# env vars
load_dotenv()
gptKey: str = os.getenv("OPENAI_API_KEY")
elevenKey: str = os.getenv("ELEVENLABS_API_KEY")
exaKey: str = os.getenv("EXA_KEY")
client: OpenAI = OpenAI(api_key=gptKey)


##Threads
microphone_event = threading.Event()
microphone_thread = threading.Thread()
pygame_thread = threading.Thread()

## pygame window initialization
screen_width = 500
screen_height = 500
pygame.init()
pygame.display.set_caption("ELO visusalizer") #title
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock() # not understanding this clock

#Audio 
CHUNK = 1024
FORMAT = pyaudio.paInt16 
CHANNELS = 1 # 1 for mono 2 for stere o?
RATE = 44100 # sample rate
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate = RATE,
                input=True,
                frames_per_buffer=CHUNK)

def get_output_level():
    data = stream.read(CHUNK, exception_on_overflow=False)
    root_mean_sq = 0 
    for i in range (0,len(data), 2):
        sample = int.from_bytes(data[i:i+2], byteorder='little', signed=True)
        root_mean_sq += sample*sample
    root_mean_sq = math.sqrt(root_mean_sq/(CHUNK/2))
    return root_mean_sq

def draw_sine_wave(amplitude):
    screen.fill((0,0,0))
    points = []
    if amplitude > 10:
        for x in range( screen_width):
            y = screen_height/2 + int(amplitude * math.sin(x*0.02))
            points.append((x,y))
    else: # draws flat line?
        points.append((0, screen_height/2))
        points.append((screen_width, screen_height/2))
    pygame.draw.lines(screen, (255, 255, 255), False, points, 2)
    pygame.display.flip()


# initialize voice components
recognizer: sr.Recognizer = sr.Recognizer()
ttsEngine: pyttsx4.Engine = pyttsx4.init()
elevenlabs.set_api_key(api_key=elevenKey)

# initialize integration components
exa: Exa = Exa(exaKey)

# Create and configure logger
today = datetime.datetime.now().__str__()
logger = logging.getLogger(__name__)

# todo: timer metrics on request completion time
# todo: GPT-4


def speak_and_print(text: str) -> None:
    stream.start_stream()
    logging.info(f"Starting stream for speak_and_print(). Stream is active: {stream.is_active()}  latency: {stream.get_input_latency()}")
    time.sleep(0.2) #adding a slight latency
    audio = elevenlabs.generate(
        text=text, voice="George", model="eleven_monolingual_v1", api_key=elevenKey
    )
    play(audio)
    print(text)
    stream.stop_stream()
    logging.info(f"Stopping stream for speak_and_print(). Stream is active: {stream.is_active()} <- should stil be active  latency: {stream.get_input_latency()}")

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
    while microphone_event.is_set():
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
    logger.info(f"Reply received: {ic(completion.choices)}")
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
    if query == "stop" :
        speak_and_print("Okay, hope I was able to help!")
        microphone_event.clear()
        microphone_thread.join()
        os._exit(0)
    elif "thanks elo that is all I needed" in query:
        speak_and_print("Okay, hope I was able to help!")
        microphone_event.clear()
        microphone_thread.join()
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

def game_loop():
    running = True
    amplitude = 100
    # whill app is running, collecet events. If one of the events is quit (X)
    # stops running
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                microphone_event.clear()

        if not stream.is_stopped() and stream.is_active():
            dampened_amp = get_output_level() / 10
            amplitude = max(10, dampened_amp)
            draw_sine_wave(amplitude)
                        
        draw_sine_wave(amplitude)
        clock.tick(60) #FPS?
    pygame.quit()


# this is the main loop for the LLM-voice part 
def conversation_loop() -> None:
    wish_me()
    while True:
        query = listen().lower()
        if not parse_keywords(query):
            text_to_model(query)
            logger.info(f"Sending {query} to LLM")
        else:
            logger.info("Skipped LLM and restarted conversation Loop")
            pass


##startup -> calibrates to audio sources, creates threads for visualizer.
def startup() -> None:
    calibrate_flag = calibrate()
    if calibrate_flag == 0:
        speak_and_print("Not able to connect to audio source")
        quit(0)
    
    pygame_thread = threading.Thread(target=game_loop)
    microphone_event.set()
    microphone_thread = threading.Thread(target=conversation_loop)
    pygame_thread.start()
    microphone_thread.start()



if __name__ == "__main__":
    startup()



