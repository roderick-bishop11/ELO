import speech_recognition as sr
import pyttsx4
import datetime

# initialize the recognizer and engine
recognizer = sr.Recognizer()
ttsEngine = pyttsx4.init()

#voice config
voices = ttsEngine.getProperty('voices')
ttsEngine.setProperty('voice', voices[140].id)

def speak(audio):
    ttsEngine.say(audio)
    ttsEngine.runAndWait()
 
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>= 0 and hour<12:
        greeting = "Good Morning, Rod! How may I help you"
  
    elif hour>= 12 and hour<18:
        greeting = "Good afternoon, Sir"
  
    else:
        greeting = "Good evening, Sir"
    print(greeting)
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
        something = ""
        speak("I cannot answer yet, but I know what you said")


def main():
    wishMe()
    query = listen()
    textToModel(query)

if __name__ == "__main__":
    main()

