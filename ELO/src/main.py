import speech_recognition as sr
from gtts import gTTS
import os
import openai

# Set your OpenAI API key
openai.api_key = 'your-api-key'

def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something:")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Error with the speech recognition service; {e}")
        return None

def chat_with_gpt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150
    )

    return response['choices'][0]['text']

def speak_text(text):
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    os.system("mpg321 output.mp3")

def main():
    while True:
        user_input = recognize_speech()

        if user_input:
            gpt_response = chat_with_gpt(user_input)
            print(f"Assistant: {gpt_response}")

            speak_text(gpt_response)

if __name__ == "__main__":
    main()