# Nova Voice Assistant - Streamlit Web Application
import streamlit as st
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
from openai import OpenAI
import threading
import time
import base64
import io

# Configure page
st.set_page_config(
    page_title="Nova Voice Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure Perplexity API
PERPLEXITY_API_KEY = "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"

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'perplexity_available' not in st.session_state:
    st.session_state.perplexity_available = False
if 'client' not in st.session_state:
    st.session_state.client = None

# Initialize Perplexity client
@st.cache_resource
def initialize_perplexity():
    try:
        client = OpenAI(
            api_key=PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        return client, True
    except Exception as e:
        st.error(f"❌ Error initializing Perplexity: {e}")
        return None, False

# Initialize TTS engine
@st.cache_resource
def initialize_tts():
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
            engine.setProperty('rate', 170)
            engine.setProperty('volume', 0.9)
        return engine
    except Exception as e:
        st.error(f"❌ Error initializing TTS: {e}")
        return None

# Load resources
client, perplexity_available = initialize_perplexity()
tts_engine = initialize_tts()

st.session_state.client = client
st.session_state.perplexity_available = perplexity_available

def query_perplexity(question):
    """Query Perplexity AI for intelligent responses"""
    if not st.session_state.perplexity_available or not st.session_state.client:
        return "Sorry, my AI brain is not available right now."
    
    try:
        response = st.session_state.client.chat.completions.create(
            model="sonar-pro",
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
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Perplexity API error: {e}")
        return "Sorry, I couldn't process that request right now. Please try again."

def speak_text(text):
    """Convert text to speech"""
    if tts_engine:
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception as e:
            st.error(f"TTS Error: {e}")

def process_command(command):
    """Process voice or text commands"""
    command = command.lower().strip()
    
    # Remove wake word if present
    if command.startswith('nova'):
        command = command.replace('nova', '').strip()
    
    # Music playback
    if 'play' in command:
        song = command.replace('play', '').strip()
        if song:
            response = f'Playing {song} on YouTube'
            try:
                pywhatkit.playonyt(song)
                return response
            except Exception as e:
                return f"Sorry, I couldn't play that song. Error: {str(e)}"
        else:
            return "What would you like me to play?"
    
    # Time query
    elif 'time' in command:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        return f'The current time is {current_time}'
    
    # Weather queries
    elif 'weather' in command:
        location = command.replace('weather', '').replace('in', '').replace('for', '').strip()
        if location:
            return query_perplexity(f"What's the current weather in {location}?")
        else:
            return query_perplexity("What's the weather like today?")
    
    # Wikipedia queries with Perplexity fallback
    elif any(phrase in command for phrase in ['who the heck is', 'who is', 'what is', 'tell me about']):
        subject = command
        for phrase in ['who the heck is', 'who is', 'what is', 'tell me about']:
            subject = subject.replace(phrase, '').strip()
        
        if subject:
            try:
                info = wikipedia.summary(subject, sentences=2)
                return info
            except wikipedia.exceptions.DisambiguationError:
                return query_perplexity(f"Tell me about {subject}")
            except wikipedia.exceptions.PageError:
                return query_perplexity(f"Tell me about {subject}")
            except Exception as e:
                return query_perplexity(f"Tell me about {subject}")
        else:
            return "What would you like to know about?"
    
    # General questions
    elif any(word in command for word in ['how', 'why', 'when', 'where', 'explain', 'define', 'calculate', 'solve', 'can you']):
        return query_perplexity(command)
    
    # News queries
    elif 'news' in command:
        return query_perplexity("What are the most important news headlines today? Please provide a brief summary.")
    
    # Math calculations
    elif any(word in command for word in ['plus', 'minus', 'multiply', 'divide', 'equals', 'math', 'calculate']):
        return query_perplexity(f"Please calculate this math problem and explain the answer: {command}")
    
    # Date queries
    elif 'date' in command and any(word in command for word in ['today', 'what', 'current']):
        today = datetime.datetime.now().strftime('%B %d, %Y')
        return f"Today is {today}"
    
    # Personal questions
    elif 'are you single' in command:
        return 'I am in a committed relationship with the internet and my data centers'
    elif 'how are you' in command:
        return 'I am doing fantastic! My circuits are buzzing with excitement to help you.'
    elif 'your name' in command:
        return 'I am Nova, your intelligent voice assistant powered by Perplexity AI'
    
    # Joke request
    elif 'joke' in command:
        try:
            joke = pyjokes.get_joke()
            return joke
        except Exception as e:
            return query_perplexity("Tell me a clean, funny joke")
    
    # System information
    elif 'about yourself' in command or 'about you' in command:
        return "I am Nova, your intelligent voice assistant powered by Perplexity AI. I can play music, answer questions, tell jokes, provide weather updates, do calculations, search the web for real-time information, and help with many other tasks."
    
    # Help command
    elif 'help' in command or 'commands' in command:
        return "I can help you with many tasks! You can ask me to play music, tell you the time or date, answer questions, get weather updates, tell jokes, do math calculations, get news updates, search for information, and much more."
    
    # Default - Use Perplexity
    else:
        if command.strip():
            return query_perplexity(command)
        else:
            return "I didn't catch that. Could you please repeat?"

def record_audio():
    """Record audio using speech recognition"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now!")
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            command = r.recognize_google(audio)
            return command
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Speech recognition error: {e}"
        except sr.WaitTimeoutError:
            return "Listening timeout"
        except Exception as e:
            return f"Error: {e}"

# Main UI
def main():
    # Header
    st.title("🤖 Nova - Advanced Voice Assistant")
    st.markdown("*Powered by Perplexity AI for real-time, accurate information*")
    
    # Status indicators
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.perplexity_available:
            st.success("✅ Perplexity AI Active")
        else:
            st.error("❌ Perplexity AI Unavailable")
    
    with col2:
        if tts_engine:
            st.success("✅ Text-to-Speech Ready")
        else:
            st.error("❌ TTS Unavailable")
    
    with col3:
        st.info(f"🕒 {datetime.datetime.now().strftime('%I:%M %p')}")
    
    st.markdown("---")
    
    # Input methods
    st.subheader("💬 Choose Input Method")
    input_method = st.radio(
        "How would you like to interact with Nova?",
        ["Text Input", "Voice Input"],
        horizontal=True
    )
    
    # Text input
    if input_method == "Text Input":
        user_input = st.text_input(
            "Type your message to Nova:",
            placeholder="e.g., 'What is the weather in New York?' or 'Tell me a joke'"
        )
        
        if st.button("Send Message", type="primary"):
            if user_input:
                # Add user message to conversation
                st.session_state.conversation_history.append({
                    "role": "user",
                    "message": user_input,
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                })
                
                # Process command
                with st.spinner("Nova is thinking..."):
                    response = process_command(user_input)
                
                # Add Nova's response
                st.session_state.conversation_history.append({
                    "role": "nova",
                    "message": response,
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                })
                
                # Speak response if TTS is available
                if st.checkbox("🔊 Enable Voice Response", value=True):
                    threading.Thread(target=speak_text, args=(response,)).start()
    
    # Voice input
    elif input_method == "Voice Input":
        st.markdown("**Click the button below and speak your command:**")
        
        if st.button("🎤 Start Voice Recording", type="primary"):
            with st.spinner("🎤 Recording... Please speak clearly"):
                voice_command = record_audio()
            
            if "error" not in voice_command.lower() and "could not" not in voice_command.lower():
                st.success(f"🎯 Heard: {voice_command}")
                
                # Add user message to conversation
                st.session_state.conversation_history.append({
                    "role": "user",
                    "message": voice_command,
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                })
                
                # Process command
                with st.spinner("Nova is processing..."):
                    response = process_command(voice_command)
                
                # Add Nova's response
                st.session_state.conversation_history.append({
                    "role": "nova",
                    "message": response,
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                })
                
                # Speak response
                threading.Thread(target=speak_text, args=(response,)).start()
            else:
                st.error(f"❌ {voice_command}")
    
    st.markdown("---")
    
    # Conversation History
    if st.session_state.conversation_history:
        st.subheader("💬 Conversation History")
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.conversation_history = []
            st.rerun()
        
        # Display conversation
        for i, msg in enumerate(reversed(st.session_state.conversation_history[-10:])):  # Show last 10 messages
            if msg["role"] == "user":
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0;">
                        <strong>👤 You ({msg['timestamp']}):</strong><br>
                        {msg['message']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #f3e5f5; padding: 10px; border-radius: 10px; margin: 5px 0;">
                        <strong>🤖 Nova ({msg['timestamp']}):</strong><br>
                        {msg['message']}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Sidebar with commands and info
    with st.sidebar:
        st.header("🎤 Voice Commands")
        st.markdown("""
        **Music & Entertainment:**
        - "Nova, play [song name]"
        - "Nova, tell me a joke"
        
        **Information:**
        - "Nova, what time is it?"
        - "Nova, what is [topic]?"
        - "Nova, who is [person]?"
        - "Nova, tell me about [subject]"
        
        **Weather & News:**
        - "Nova, what's the weather in [city]?"
        - "Nova, what's the latest news?"
        
        **Calculations:**
        - "Nova, calculate 25 plus 30"
        - "Nova, what is 15% of 200?"
        
        **Personal:**
        - "Nova, how are you?"
        - "Nova, what is your name?"
        - "Nova, about yourself"
        
        **General:**
        - "Nova, explain [concept]"
        - "Nova, help"
        """)
        
        st.markdown("---")
        st.markdown("**🔧 Settings**")
        
        # API Status
        st.markdown(f"**Perplexity API:** {'🟢 Active' if st.session_state.perplexity_available else '🔴 Inactive'}")
        
        # Current time
        if st.button("🔄 Refresh"):
            st.rerun()

if __name__ == "__main__":
    main()
