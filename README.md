# AI Support Assistant with Voice Capabilities

A production-ready AI-powered Support Assistant with voice conversation capabilities, multilingual support, and intelligent query escalation.

## 🌟 Features

- **AI-Powered Conversations**: Natural, fluent conversations using GPT-4
- **Voice Assistant**: Speech-to-text and text-to-speech for hands-free interaction
- **Multilingual Support**: Supports 10+ languages with automatic detection
- **FAQ Resolution**: Intelligent FAQ matching and resolution
- **Smart Escalation**: Automatically escalates complex queries to human agents
- **Real-time Chat**: Interactive chatbot interface
- **Conversation History**: Maintains context throughout the conversation
- **Streamlit Dashboard**: Clean, professional web interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Microphone (for voice features)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd ai-agent-1
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
```

4. Run the application:
```bash
streamlit run app.py
```

5. Open your browser to `http://localhost:8501`

## 📁 Project Structure

```
ai-agent-1/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── backend/
│   └── app/
│       └── core/
│           ├── ai_assistant.py        # Core AI logic
│           ├── voice_handler.py       # Voice processing
│           ├── language_handler.py    # Multilingual support
│           └── faq_database.py        # FAQ management
└── README.md
```

## 🎯 Usage

### Text Chat Mode
1. Select your preferred language from the sidebar
2. Type your question in the chat input
3. The AI will respond with relevant answers or escalate if needed

### Voice Chat Mode
1. Enable "Voice Mode" in the sidebar
2. Click "Start Recording" to speak your question
3. The AI will transcribe, process, and respond with voice

### Supported Languages
- English, Spanish, French, German, Italian
- Portuguese, Hindi, Chinese, Japanese, Arabic

## 🔧 Configuration

Edit `config.py` to customize:
- AI model and parameters
- Supported languages
- Escalation keywords
- FAQ categories
- Voice settings

## 📊 Features in Detail

### FAQ Resolution
The assistant can handle common questions about:
- General information
- Technical support
- Billing and payments
- Account management
- Product features
- Troubleshooting

### Smart Escalation
Automatically escalates when detecting:
- Complex technical issues
- Billing disputes
- Legal matters
- Customer complaints
- Urgent requests
- Keywords like "speak to human"

### Multilingual Support
- Automatic language detection
- Real-time translation
- Context-aware responses in user's language

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add your API keys in the Secrets section
5. Deploy!

### Deploy to Heroku

```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
```

### Deploy with Docker

```bash
docker build -t support-assistant .
docker run -p 8501:8501 support-assistant
```

## 🔐 Security

- Never commit `.env` file
- Keep API keys secure
- Use environment variables for sensitive data
- Implement rate limiting for production

## 📝 License

MIT License - Feel free to use for commercial projects

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📧 Support

For issues or questions, please open a GitHub issue.
