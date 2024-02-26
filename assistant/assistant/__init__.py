import speech_recognition as sr
import pyttsx4
import datetime
from openai import OpenAI
import elevenlabs
from elevenlabs import play
import os
from dotenv import load_dotenv

load_dotenv()

gptKey = os.getenv("OPENAI_API_KEY")
elevenKey = os.getenv("ELEVENLABS_API_KEY")
client = OpenAI(api_key=gptKey)
elevenlabs.set_api_key(api_key=elevenKey)

# initialize the recognizer and engine
recognizer = sr.Recognizer()
ttsEngine = pyttsx4.init()


def speak(text):

    audio = elevenlabs.generate(
            text=text, voice="Adam", model="eleven_monolingual_v1", api_key=elevenKey
        )
    play(audio)
    # ttsEngine.say(audio)
    # ttsEngine.runAndWait()
 
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>= 0 and hour<12:
        greeting = "Good Morning, Rod! How may I help you"
  
    elif hour>= 12 and hour<18:
        greeting = "Good afternoon, Sir"
  
    else:
        greeting = "Good evening, Sir"
    speak(greeting)

# the assistant will listen to you, go speech to text.
def listen():
    with sr.Microphone(device_index=1) as source:
         
        print("Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)
  
    try:
        print("Recognizing...")    
        query = recognizer.recognize_google(audio, language ='en-in')
        print(f"User said: {query}\n")
  
    except Exception as e:
        print(e)    
        print("Unable to Recognize your voice.")  
        return "None"
     
    return query

#submit text to LLM
def textToModel(query):
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
     messages=[
        {"role": "system", "content": "You are a personal assistant, named ELO. ELO stands for Enhanced Logical Operative."},
        {"role": "user", "content": query}
        ]
    )
    reply = completion.choices[0].message.content
    print(reply)
    speak(reply)

def listenForStop(query):
    if query == "stop":
        speak("Okay, hope I was able to help!")
        exit()
    elif query == "Thanks ELO that is all I needed":
        speak("Okay, hope I was able to help!")
        exit()

def main():
    wishMe()
    while True:
        query = listen()
        listenForStop(query)
        textToModel(query)

if __name__ == "__main__":
    main()

