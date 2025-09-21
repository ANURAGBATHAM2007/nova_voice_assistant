# Voice Assistant with Perplexity API Integration - Nova Edition
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
from openai import OpenAI

# Configure Perplexity API
PERPLEXITY_API_KEY = "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"

# Initialize Perplexity client (OpenAI-compatible)
try:
    client = OpenAI(
        api_key=PERPLEXITY_API_KEY,
        base_url="https://api.perplexity.ai"
    )
    print("✅ Perplexity API initialized successfully!")
    PERPLEXITY_AVAILABLE = True
except Exception as e:
    print(f"❌ Error initializing Perplexity: {e}")
    PERPLEXITY_AVAILABLE = False

# Initialize speech recognition and text-to-speech
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Check if voices are available before setting
if voices:
    # Set to female voice if available (index 1 is typically female)
    engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
    # Optimize speech settings
    engine.setProperty('rate', 170)  # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
else:
    print("⚠️ No voices available, using default voice")

def talk(text):
    """Convert text to speech and print for debugging"""
    print(f"Nova: {text}")
    engine.say(text)
    engine.runAndWait()

def query_perplexity(question):
    """Query Perplexity AI for intelligent responses"""
    if not PERPLEXITY_AVAILABLE:
        return "Sorry, my AI brain is not available right now."
    
    try:
        response = client.chat.completions.create(
            model="sonar-pro",  # Using Perplexity's most advanced model
            messages=[
                {
                    "role": "system",
                    "content": "You are Nova, an intelligent and helpful voice assistant. Respond in a natural, conversational way. Keep responses brief (2-3 sentences max) and suitable for speech. Be friendly, informative, and concise."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=150,  # Limit response length for voice
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Perplexity API error: {e}")
        return "Sorry, I couldn't process that request right now. Please try again."

def take_command():
    """Listen to voice commands and convert them to text"""
    command = ""
    try:
        with sr.Microphone() as source:
            print('🎤 Listening...')
            # Adjust for ambient noise with longer duration for better accuracy
            listener.adjust_for_ambient_noise(source, duration=1.5)
            # Listen for voice with increased timeout
            voice = listener.listen(source, timeout=6, phrase_time_limit=8)
            command = listener.recognize_google(voice)
            command = command.lower()
            
            # Check for wake word "nova"
            if 'nova' in command:
                command = command.replace('nova', '').strip()
                print(f"✅ Command received: {command}")
            else:
                print(f"⚠️ Wake word 'Nova' not detected. Heard: {command}")
                return ""
                
    except sr.UnknownValueError:
        print("❌ Could not understand audio - please speak clearly")
        return ""
    except sr.RequestError as e:
        print(f"❌ Speech recognition service error: {e}")
        return ""
    except sr.WaitTimeoutError:
        print("⏰ Listening timeout - no speech detected")
        return ""
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return ""
    
    return command

def run_nova():
    """Main function that processes voice commands with Perplexity AI integration"""
    command = take_command()
    
    if command == "":
        return True  # Continue the loop
    
    print(f"🔄 Processing command: {command}")
    
    # Music playback
    if 'play' in command:
        song = command.replace('play', '').strip()
        if song:
            talk(f'Playing {song} on YouTube')
            try:
                pywhatkit.playonyt(song)
            except Exception as e:
                print(f"Error playing song: {e}")
                talk("Sorry, I couldn't play that song. Please check your internet connection.")
        else:
            talk("What would you like me to play?")
    
    # Time query
    elif 'time' in command:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        talk(f'The current time is {current_time}')
    
    # Weather queries - Enhanced with Perplexity
    elif 'weather' in command:
        location = command.replace('weather', '').replace('in', '').replace('for', '').strip()
        if location:
            perplexity_response = query_perplexity(f"What's the current weather in {location}?")
        else:
            perplexity_response = query_perplexity("What's the weather like today?")
        talk(perplexity_response)
    
    # Wikipedia queries with Perplexity fallback
    elif any(phrase in command for phrase in ['who the heck is', 'who is', 'what is', 'tell me about']):
        # Extract the subject from the command
        subject = command
        for phrase in ['who the heck is', 'who is', 'what is', 'tell me about']:
            subject = subject.replace(phrase, '').strip()
        
        if subject:
            try:
                # Try Wikipedia first for factual information
                info = wikipedia.summary(subject, sentences=2)
                talk(info)
            except wikipedia.exceptions.DisambiguationError:
                # Use Perplexity for disambiguation
                perplexity_response = query_perplexity(f"Tell me about {subject}")
                talk(perplexity_response)
            except wikipedia.exceptions.PageError:
                # Fallback to Perplexity if Wikipedia doesn't have the information
                perplexity_response = query_perplexity(f"Tell me about {subject}")
                talk(perplexity_response)
            except Exception as e:
                print(f"Wikipedia error: {e}")
                # Fallback to Perplexity
                perplexity_response = query_perplexity(f"Tell me about {subject}")
                talk(perplexity_response)
        else:
            talk("What would you like to know about?")
    
    # General questions - Use Perplexity AI
    elif any(word in command for word in ['how', 'why', 'when', 'where', 'explain', 'define', 'calculate', 'solve', 'can you']):
        talk("Let me search for that information...")
        perplexity_response = query_perplexity(command)
        talk(perplexity_response)
    
    # News queries
    elif 'news' in command:
        talk("Getting the latest news for you...")
        perplexity_response = query_perplexity("What are the most important news headlines today? Please provide a brief summary.")
        talk(perplexity_response)
    
    # Math calculations
    elif any(word in command for word in ['plus', 'minus', 'multiply', 'divide', 'equals', 'math', 'calculate']):
        perplexity_response = query_perplexity(f"Please calculate this math problem and explain the answer: {command}")
        talk(perplexity_response)
    
    # Date queries
    elif 'date' in command and any(word in command for word in ['today', 'what', 'current']):
        today = datetime.datetime.now().strftime('%B %d, %Y')
        talk(f"Today is {today}")
    
    # Personal questions (humorous responses)
    elif 'are you single' in command:
        talk('I am in a committed relationship with the internet and my data centers')
    elif 'how are you' in command:
        talk('I am doing fantastic! My circuits are buzzing with excitement to help you.')
    elif 'your name' in command:
        talk('I am Nova, your intelligent voice assistant powered by Perplexity AI')
    
    # Joke request
    elif 'joke' in command:
        try:
            joke = pyjokes.get_joke()
            talk(joke)
        except Exception as e:
            print(f"Error getting joke: {e}")
            # Fallback to Perplexity for jokes
            perplexity_response = query_perplexity("Tell me a clean, funny joke")
            talk(perplexity_response)
    
    # System information
    elif 'about yourself' in command or 'about you' in command:
        talk("I am Nova, your intelligent voice assistant powered by Perplexity AI. I can play music, answer questions, tell jokes, provide weather updates, do calculations, search the web for real-time information, and help with many other tasks.")
    
    # Help command
    elif 'help' in command or 'commands' in command:
        help_text = "I can help you with many tasks! You can ask me to play music, tell you the time or date, answer questions, get weather updates, tell jokes, do math calculations, get news updates, search for information, and much more. Just say Nova followed by your request."
        talk(help_text)
    
    # Exit commands
    elif any(word in command for word in ['stop', 'exit', 'quit', 'goodbye', 'bye', 'shut down', 'sleep']):
        talk("Goodbye! It was great helping you today. Have a wonderful time!")
        return False
    
    # Default - Use Perplexity for general conversation
    else:
        if command.strip():  # Only process non-empty commands
            perplexity_response = query_perplexity(command)
            talk(perplexity_response)
        else:
            talk("I didn't catch that. Could you please repeat?")
    
    return True

# Main execution with enhanced error handling
if __name__ == "__main__":
    print("🚀 Nova - Advanced Voice Assistant with Perplexity AI")
    print("=" * 65)
    
    # Welcome message based on Perplexity availability
    if PERPLEXITY_AVAILABLE:
        talk("Hello! I am Nova, your advanced voice assistant powered by Perplexity AI. Say Nova followed by your command to get started.")
        print("✅ Perplexity AI integration active - Real-time search intelligence available!")
    else:
        talk("Hello! I am Nova, your voice assistant. Say Nova followed by your command to get started.")
        print("⚠️ Perplexity AI not available - Basic features only")
    
    # Display available commands
    print("\n🎤 Voice Commands you can try:")
    print("- 'Nova, play [song name]' - Play music on YouTube")
    print("- 'Nova, what time is it?' - Get current time")
    print("- 'Nova, who is [person]?' - Get information about someone")
    print("- 'Nova, what's the weather in [city]?' - Get weather info")
    print("- 'Nova, tell me a joke' - Hear a funny joke")
    print("- 'Nova, calculate 25 plus 30' - Do math calculations")
    print("- 'Nova, what's the latest news?' - Get real-time news updates")
    print("- 'Nova, search for [topic]' - Search the web for information")
    print("- 'Nova, how are you?' - Chat with me")
    print("- 'Nova, help' - Get list of commands")
    print("- 'Nova, goodbye' - Exit the assistant")
    print("\n" + "=" * 65)
    print("💡 Tip: Speak clearly and wait for the listening indicator!")
    print("🌐 Powered by Perplexity AI for real-time, accurate information!")
    print("=" * 65 + "\n")
    
    try:
        # Main loop
        while True:
            if not run_nova():
                break
    except KeyboardInterrupt:
        print("\n\n🛑 Voice assistant interrupted by user...")
        talk("Goodbye! Nova signing off.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        talk("I encountered an error. Please restart me when you're ready.")
    finally:
        print("👋 Thank you for using Nova!")
