# Setup Guide - AI Support Assistant

## 📋 Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher installed
- pip (Python package installer)
- Git (for version control)
- An OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- A microphone (optional, for voice features)

---

## 🚀 Quick Setup (5 minutes)

### 1. Clone or Download the Project

If you have Git:
```bash
git clone <your-repo-url>
cd ai-agent-1
```

Or download and extract the ZIP file.

### 2. Create Virtual Environment (Recommended)

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- Streamlit (web interface)
- OpenAI (AI capabilities)
- SpeechRecognition (voice input)
- gTTS (text-to-speech)
- Deep-Translator (multilingual support)
- And more...

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,es,fr,de,it,pt,hi,zh,ja,ar
```

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## 🔧 Detailed Setup

### Getting Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to "API Keys" in your account settings
4. Click "Create new secret key"
5. Copy the key (you won't be able to see it again!)
6. Paste it in your `.env` file

**Important:** 
- Never share your API key publicly
- Never commit `.env` file to Git
- Add credits to your OpenAI account if needed

### Installing Python Dependencies

If you encounter issues during installation:

**For audio/voice features on Windows:**
```powershell
pip install pipwin
pipwin install pyaudio
```

**For audio/voice features on Mac:**
```bash
brew install portaudio
pip install pyaudio
```

**For audio/voice features on Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### Microphone Setup

For voice features to work:

1. **Windows:** Allow microphone access in Settings > Privacy > Microphone
2. **Mac:** Allow terminal access in System Preferences > Security & Privacy > Microphone
3. **Browser:** Grant microphone permissions when prompted

### Testing Your Setup

After running the app:

1. ✅ Check if the interface loads
2. ✅ Try typing a message in the chat
3. ✅ Test language switching in the sidebar
4. ✅ Enable voice mode (if microphone available)
5. ✅ Try voice input

---

## 📁 Project Structure

```
ai-agent-1/
│
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .env                           # Your actual environment variables (create this)
│
├── backend/
│   └── app/
│       └── core/
│           ├── ai_assistant.py         # AI conversation logic
│           ├── voice_handler.py        # Voice processing
│           ├── language_handler.py     # Multilingual support
│           └── faq_database.py         # FAQ database
│
├── README.md                       # Project documentation
├── DEPLOYMENT.md                   # Deployment guide
├── SETUP.md                        # This file
├── Dockerfile                      # Docker configuration
├── docker-compose.yml             # Docker Compose setup
└── Procfile                       # Heroku deployment
```

---

## 🎯 Configuration Options

### In `config.py`:

```python
# AI Model Settings
AI_MODEL = "gpt-4-turbo-preview"  # or "gpt-3.5-turbo" for faster/cheaper
TEMPERATURE = 0.7                  # Response creativity (0-1)
MAX_TOKENS = 500                   # Response length limit

# Language Settings
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {...}        # Add/remove languages

# Escalation Keywords
ESCALATION_KEYWORDS = [...]        # Customize trigger words
```

### Customizing FAQs

Edit `backend/app/core/faq_database.py` to:
- Add your own FAQ categories
- Customize questions and answers
- Add industry-specific keywords

Example:
```python
"Your Category": [
    {
        "question": "Your question?",
        "answer": "Your answer.",
        "keywords": ["keyword1", "keyword2"]
    }
]
```

---

## 🔍 Troubleshooting

### Common Issues

**1. "ModuleNotFoundError"**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**2. "OpenAI API key not configured"**
- Check if `.env` file exists
- Verify API key format (starts with 'sk-')
- Restart the application

**3. "Microphone not available"**
- Check microphone connection
- Grant permissions
- Try a different browser
- Voice features optional - text chat still works

**4. "Port 8501 already in use"**
```bash
# Use a different port
streamlit run app.py --server.port=8502
```

**5. Import errors with speech recognition:**
```bash
# Windows
pip install pyaudio-wheel
# or
pip install pipwin
pipwin install pyaudio

# Mac/Linux
brew install portaudio
pip install pyaudio
```

### Debug Mode

Run with debug output:
```bash
streamlit run app.py --logger.level=debug
```

### Testing Without Voice

If voice features aren't working, you can disable them:
1. Don't toggle "Enable Voice Mode"
2. Use text input only
3. All other features will work perfectly

---

## 💡 Tips & Best Practices

### Development

1. **Use a virtual environment** - Keeps dependencies isolated
2. **Keep .env secure** - Never commit to version control
3. **Monitor API usage** - Check OpenAI dashboard regularly
4. **Test in different browsers** - Chrome/Edge work best

### API Costs

- GPT-4: ~$0.03 per 1K tokens (more expensive but better quality)
- GPT-3.5-Turbo: ~$0.002 per 1K tokens (cheaper, faster)
- Average conversation: $0.05-0.20 with GPT-4
- Voice features: Free (using Google services)

### Performance

- FAQ responses are instant (no API cost)
- AI responses take 2-5 seconds
- Voice processing adds 1-2 seconds
- Conversation history improves context

---

## 🚀 Next Steps

After setup:

1. **Customize FAQs** - Add your business-specific questions
2. **Test thoroughly** - Try different scenarios
3. **Adjust settings** - Fine-tune in `config.py`
4. **Deploy** - See `DEPLOYMENT.md` for hosting options
5. **Monitor** - Track usage and improve

---

## 📞 Getting Help

If you encounter issues:

1. Check this setup guide
2. Review error messages carefully
3. Check OpenAI status page
4. Verify all dependencies installed
5. Try with a fresh virtual environment

---

## 🎉 You're Ready!

Once you see the application running:

1. Try asking "What are your business hours?"
2. Test language switching
3. Enable voice mode
4. Browse FAQ categories
5. Test escalation by typing "speak to a human"

Enjoy your AI Support Assistant! 🤖
