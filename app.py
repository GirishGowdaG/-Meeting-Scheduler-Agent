"""
AI Support Assistant with Voice - Main Streamlit Application
"""
import streamlit as st
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.core.ai_assistant import AIAssistant
from backend.app.core.voice_handler import VoiceHandler
from backend.app.core.language_handler import LanguageHandler
import config


# Page configuration
st.set_page_config(
    page_title="AI Support Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #000000;
        margin-left: 20%;
        color: #FFFFFF !important;
    }
    .assistant-message {
        background-color: #000000;
        margin-right: 20%;
        color: #FFFFFF !important;
    }
    .escalation-message {
        background-color: #000000;
        border-left: 4px solid #ffc107;
        color: #FFFFFF !important;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 5px;
        margin: 1rem 0;
        color: #155724 !important;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 5px;
        margin: 1rem 0;
        color: #0c5460 !important;
    }
    .stButton>button {
        width: 100%;
        color: #000000 !important;
    }
    /* Sidebar text */
    .css-1d391kg, .css-1d391kg p, .css-1d391kg span, .css-1d391kg label {
        color: #000000 !important;
    }
    /* Main content area */
    .stMarkdown {
        color: #000000 !important;
    }
    /* Chat input */
    .stChatInput input {
        color: #000000 !important;
    }
    /* Expander text */
    .streamlit-expanderHeader {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if "ai_assistant" not in st.session_state:
        st.session_state.ai_assistant = AIAssistant()
    
    if "voice_handler" not in st.session_state:
        st.session_state.voice_handler = VoiceHandler()
    
    if "language_handler" not in st.session_state:
        st.session_state.language_handler = LanguageHandler()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "language" not in st.session_state:
        st.session_state.language = "en"
    
    if "voice_mode" not in st.session_state:
        st.session_state.voice_mode = False
    
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False


def render_sidebar():
    """Render sidebar with settings and controls"""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # Language selection
        st.subheader("🌍 Language")
        languages = st.session_state.language_handler.get_all_supported_languages()
        
        selected_lang = st.selectbox(
            "Select Language",
            options=list(languages.keys()),
            format_func=lambda x: f"{languages[x]} ({x.upper()})",
            index=list(languages.keys()).index(st.session_state.language)
        )
        
        if selected_lang != st.session_state.language:
            st.session_state.language = selected_lang
            st.rerun()
        
        st.divider()
        
        # Voice mode toggle
        st.subheader("🎤 Voice Assistant")
        
        voice_available = st.session_state.voice_handler.is_microphone_available()
        
        if voice_available:
            voice_mode = st.toggle(
                "Enable Voice Mode",
                value=st.session_state.voice_mode,
                help="Enable to use voice input and output"
            )
            st.session_state.voice_mode = voice_mode
            
            if voice_mode:
                st.success("✅ Voice mode active")
        else:
            st.warning("⚠️ Microphone not detected")
            st.info("Voice features require a working microphone")
        
        st.divider()
        
        # Chat controls
        st.subheader("💬 Chat Controls")
        
        if st.button("🔄 Reset Conversation", use_container_width=True):
            st.session_state.ai_assistant.reset_conversation()
            st.session_state.messages = []
            st.session_state.conversation_started = False
            st.success("Conversation reset!")
            st.rerun()
        
        if st.button("📋 Export Chat", use_container_width=True):
            if st.session_state.messages:
                summary = st.session_state.ai_assistant.get_conversation_summary()
                st.download_button(
                    label="Download Transcript",
                    data=summary,
                    file_name=f"chat_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            else:
                st.info("No conversation to export")
        
        st.divider()
        
        # FAQ Browser
        st.subheader("📚 FAQ Categories")
        categories = st.session_state.ai_assistant.faq_db.get_all_categories()
        
        selected_category = st.selectbox("Browse FAQs", [""] + categories)
        
        if selected_category:
            faqs = st.session_state.ai_assistant.faq_db.get_faqs_by_category(selected_category)
            with st.expander(f"View {selected_category} FAQs"):
                for faq in faqs:
                    st.markdown(f"**Q: {faq['question']}**")
                    st.markdown(f"A: {faq['answer']}")
                    st.divider()
        
        st.divider()
        
        # Status info
        st.subheader("ℹ️ System Status")
        st.caption(f"🤖 Model: {config.AI_MODEL}")
        st.caption(f"🌐 Language: {languages[st.session_state.language]}")
        st.caption(f"🎤 Voice: {'Enabled' if st.session_state.voice_mode else 'Disabled'}")
        
        # API Key check
        if not config.OPENAI_API_KEY:
            st.error("⚠️ OpenAI API key not configured")
            st.info("Add your API key to the .env file")


def display_message(role: str, content: str, metadata: dict = None):
    """Display a chat message"""
    if role == "user":
        st.markdown(f'<div class="chat-message user-message">👤 You: {content}</div>', unsafe_allow_html=True)
    elif role == "assistant":
        if metadata and metadata.get("escalated"):
            st.markdown(f'<div class="chat-message escalation-message">🤖 Assistant: {content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message">🤖 Assistant: {content}</div>', unsafe_allow_html=True)
            
            # Show metadata if available
            if metadata:
                with st.expander("ℹ️ Response Details", expanded=False):
                    st.json(metadata)


def process_user_input(user_input: str):
    """Process user input and generate response"""
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Get AI response
    with st.spinner("Thinking..."):
        response_data = st.session_state.ai_assistant.process_query(
            user_input,
            st.session_state.language
        )
    
    # Add assistant response to chat
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_data["response"],
        "metadata": response_data.get("metadata", {}),
        "timestamp": datetime.now()
    })
    
    # Generate voice output if voice mode is enabled
    if st.session_state.voice_mode and config.VOICE_ENABLED:
        audio_file = st.session_state.voice_handler.text_to_speech(
            response_data["response"],
            st.session_state.language
        )
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
            # Clean up temp file after playing
            st.session_state.voice_handler.cleanup_temp_file(audio_file)


def render_chat_interface():
    """Render main chat interface"""
    # Display welcome message if conversation not started
    if not st.session_state.conversation_started:
        greeting = st.session_state.language_handler.get_greeting(st.session_state.language)
        
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown(f"### {greeting}")
        st.markdown("I'm your AI-powered support assistant. I can help you with:")
        st.markdown("- 📖 Frequently asked questions")
        st.markdown("- 🛠️ Technical support")
        st.markdown("- 💳 Billing inquiries")
        st.markdown("- 👤 Account management")
        st.markdown("- 🎯 Product information")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.session_state.voice_mode:
            voice_msg = st.session_state.language_handler.get_voice_confirmation(st.session_state.language)
            st.info(f"🎤 {voice_msg}")
        
        st.session_state.conversation_started = True
    
    # Display chat messages
    for message in st.session_state.messages:
        display_message(
            message["role"],
            message["content"],
            message.get("metadata")
        )
    
    # Voice input button
    if st.session_state.voice_mode:
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("🎤 Record Voice", use_container_width=True):
                with st.spinner("Listening... Speak now!"):
                    success, result = st.session_state.voice_handler.speech_to_text(
                        st.session_state.language
                    )
                
                if success:
                    st.success(f"Recognized: {result}")
                    process_user_input(result)
                    st.rerun()
                else:
                    st.error(f"Error: {result}")
    
    # Text input
    user_input = st.chat_input("Type your message here..." if not st.session_state.voice_mode else "Type or use voice input...")
    
    if user_input:
        process_user_input(user_input)
        st.rerun()


def main():
    """Main application function"""
    # Initialize session state
    init_session_state()
    
    # Header
    st.markdown('<div class="main-header">🤖 AI Support Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Sales, Marketing & Support with Voice AI</div>', unsafe_allow_html=True)
    
    # Check API key
    if not config.OPENAI_API_KEY:
        st.error("⚠️ OpenAI API Key not configured!")
        st.info("Please add your OpenAI API key to the .env file:")
        st.code("OPENAI_API_KEY=your_api_key_here")
        
        with st.expander("How to get an API key"):
            st.markdown("""
            1. Go to [OpenAI Platform](https://platform.openai.com/)
            2. Sign up or log in
            3. Navigate to API Keys section
            4. Create a new API key
            5. Copy and paste it in your .env file
            """)
        return
    
    # Render sidebar
    render_sidebar()
    
    # Render main chat interface
    render_chat_interface()
    
    # Footer
    st.divider()
    st.caption("Powered by OpenAI GPT-4 | Built with Streamlit | © 2025")


if __name__ == "__main__":
    main()
