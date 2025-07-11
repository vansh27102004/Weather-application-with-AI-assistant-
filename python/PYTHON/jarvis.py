import pyttsx3
import speech_recognition as sr
import os
import datetime
import time
import requests   # Import subprocess for opening the GUI
import subprocess


# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 180)

def speak(text):
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-IN')
        print(f"You said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Didn't catch that. Try again.")
        return ""
    except sr.RequestError:
        speak("Network error.")
        return ""

def get_weather_data(city):
    try:
        api_key = "2894fe5fb6d0d510ab4faa71f8bd8913"  # Make sure to keep your API key secure
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        data = requests.get(url).json()
        if data["cod"] != 200:
            return {"error": "City not found"}

        weather = data["weather"][0]["main"].capitalize()
        desc = data["weather"][0]["description"].capitalize()
        temp = int(data["main"]["temp"] - 273.15)  # Convert Kelvin to Celsius
        pressure = data["main"]["pressure"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%I:%M %p")
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%I:%M %p")

        return {
            "Weather": weather,
            "Description": desc,
            "Temperature": f"{temp} °C",
            "Pressure": f"{pressure} hPa",
            "Humidity": f"{humidity}%",
            "Wind Speed": f"{wind_speed} m/s",
            "Sunrise": sunrise,
            "Sunset": sunset
        }

    except Exception as e:
        print(f"Error fetching weather data: {e}")  # Log the error for debugging
        return {"error": "Unable to fetch weather"}

def open_vscode():
    speak("Opening Visual Studio Code")
    os.system("code")

def jarvis():
    speak("Hello User, Jarvis is online. How can I assist you today?")
    while True:
    
        query = take_command()
        print('DEBUG:', query)
        command_found = False

        if "hello jarvis" in query:
            speak("Hello sir ,how may i help you today?")
            command_found = True

        elif "what is the time" in query:
            time_now = datetime.datetime.now().strftime("%I:%M %p")
            speak("The current time is " + time_now)
            command_found = True

        elif "what is the date" in query:
            date_today = datetime.datetime.now().strftime("%A, %d %B %Y")
            speak("Today's date is " + date_today)
            command_found = True

        elif "open vs code" in query:
            open_vscode()
            command_found = True
               
            
        elif "can you explain your code" in query or "explain your code" in query:
            speak ("In my code am programmed to do several commands like :- .  a voice-activated program that uses the pyttsx3 library for text-to-speech functionality, allowing me to respond verbally to user commands. I listen for voice input through the take_command() function, which utilizes Google's speech recognition to convert speech into text. I can fetch current weather data for a specified city using the OpenWeatherMap API through the get_weather_data(city) function, which retrieves information like temperature and humidity. Additionally, I can open applications like Visual Studio Code with the open_vscode() function. My main logic is contained in the jarvis() function, which continuously listens for commands, processes them, and executes the appropriate actions, including providing the time, date, and weather information. The explain_code() function allows me to explain my functionality when prompted, summarizing my capabilities and how I operate.")


    
        elif "exit" in query or "quit" in query:
            speak("Shutting down. Goodbye.")
            break

       
        elif "weather" in query and ("app" in query or "application" in query):
            speak("Please tell me the city name.")
            city = ""
            attempts = 0
            while not city and attempts < 2:
                city = take_command()
                print("[DEBUG] City received:", city)
                attempts += 1 
                if city:
                    speak(f"Fetching weather for {city}")
                    data = get_weather_data(city)
                    print("[DEBUG] Weather data:", data)

                    if "error" in data:
                        speak(data["error"])
                    else:
                        # Save weather details to a temporary file
                        with open("weather.txt", "w") as f:
                            for key, value in data.items():
                                f.write(f"{key}: {value}\n")

                        # Launch the GUI using subprocess
                        print("Attempting to open the weather app...")
                        subprocess.Popen(["python", "project.py", city])
                        print("Weather app should now be open.")

                        # Wait for GUI to load (3–4 seconds)
                        time.sleep(4)

                        # Speak weather info once GUI is visible
                        speak("Here is the weather report:")
                        for key, value in data.items():
                            speak(f"{key}: {value}")
                            time.sleep(0.3)

                    command_found = True
                    break
            if not city:
                speak("Sorry, I couldn't understand the city name.")
                command_found = True

        elif "introduce yourself" in query:
            speak("okay. So i am jarvis an ai assistant and i am the part of the capstone project of group number 60. Our capstone project is Weather application with ai assistant. in our group there are three members , Pushkar pandey ,who developed the GUI (graphical user interface) of the application and than sameer panwar who develops ai assistant(me) and shreya pandey ,basically in overall project she learns about whole project and helped us wherever we needed. so that's our project. Thankyou")   
            command_found = True

        elif "exit" in query or "quit" in query:
            speak("Shutting down. Goodbye user.")
            break

if __name__== "__main__":
    jarvis()                                               
