# Deployment Guide - AI Support Assistant

## 🚀 Deployment Options

This guide covers multiple deployment options for your AI Support Assistant.

---

## 1. Streamlit Cloud (Recommended - Free & Easy)

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
- OpenAI API key

### Steps

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI Support Assistant"
   git branch -M main
   git remote add origin https://github.com/yourusername/ai-support-assistant.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Advanced settings"

3. **Add Secrets**
   In the Secrets section, add:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   DEFAULT_LANGUAGE = "en"
   ```

4. **Deploy**
   - Click "Deploy!"
   - Wait 2-3 minutes for deployment
   - Your app will be live at `https://your-app-name.streamlit.app`

---

## 2. Heroku Deployment

### Prerequisites
- Heroku account
- Heroku CLI installed

### Steps

1. **Create Procfile**
   ```bash
   echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile
   ```

2. **Create runtime.txt**
   ```bash
   echo "python-3.11.5" > runtime.txt
   ```

3. **Deploy to Heroku**
   ```bash
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your_api_key_here
   git push heroku main
   heroku open
   ```

4. **Scale the app**
   ```bash
   heroku ps:scale web=1
   ```

---

## 3. Docker Deployment

### Create Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build image
docker build -t ai-support-assistant .

# Run container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_api_key_here \
  ai-support-assistant
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEFAULT_LANGUAGE=en
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

---

## 4. AWS EC2 Deployment

### Steps

1. **Launch EC2 Instance**
   - Choose Ubuntu 22.04 LTS
   - Instance type: t2.medium or larger
   - Open port 8501 in security group

2. **SSH into instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv portaudio19-dev -y
   ```

4. **Clone and setup**
   ```bash
   git clone https://github.com/yourusername/ai-support-assistant.git
   cd ai-support-assistant
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Create .env file**
   ```bash
   nano .env
   # Add your API keys
   ```

6. **Run with systemd**
   Create `/etc/systemd/system/ai-assistant.service`:
   ```ini
   [Unit]
   Description=AI Support Assistant
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/ai-support-assistant
   Environment="PATH=/home/ubuntu/ai-support-assistant/venv/bin"
   ExecStart=/home/ubuntu/ai-support-assistant/venv/bin/streamlit run app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable ai-assistant
   sudo systemctl start ai-assistant
   ```

---

## 5. Azure App Service

### Steps

1. **Install Azure CLI**
   ```bash
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   ```

2. **Login and create resources**
   ```bash
   az login
   az group create --name ai-assistant-rg --location eastus
   az appservice plan create --name ai-assistant-plan --resource-group ai-assistant-rg --sku B1 --is-linux
   ```

3. **Create web app**
   ```bash
   az webapp create --resource-group ai-assistant-rg --plan ai-assistant-plan --name your-app-name --runtime "PYTHON:3.11"
   ```

4. **Configure environment**
   ```bash
   az webapp config appsettings set --resource-group ai-assistant-rg --name your-app-name --settings OPENAI_API_KEY=your_key
   ```

5. **Deploy**
   ```bash
   az webapp up --name your-app-name --resource-group ai-assistant-rg
   ```

---

## 6. Google Cloud Run

### Steps

1. **Create Dockerfile** (use Docker section above)

2. **Build and push to GCR**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/ai-assistant
   ```

3. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy ai-assistant \
     --image gcr.io/PROJECT_ID/ai-assistant \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=your_key
   ```

---

## Environment Variables

Required environment variables for all deployments:

```bash
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,es,fr,de,it,pt,hi,zh,ja,ar
```

Optional:
```bash
ELEVENLABS_API_KEY=your_elevenlabs_key  # For premium voice
AI_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.7
MAX_TOKENS=500
```

---

## Production Considerations

### Security
- Use HTTPS (most platforms provide this automatically)
- Store API keys in environment variables, never in code
- Implement rate limiting
- Add authentication if needed

### Performance
- Use caching for FAQ responses
- Implement connection pooling
- Monitor API usage and costs
- Set timeout limits

### Monitoring
- Set up application logging
- Monitor API usage
- Track response times
- Set up alerts for errors

### Scaling
- Use horizontal scaling for high traffic
- Implement load balancing
- Consider CDN for static assets
- Cache frequently accessed data

---

## Testing Deployment

After deployment, test:

1. ✅ Application loads correctly
2. ✅ Chat functionality works
3. ✅ Voice mode (if microphone available)
4. ✅ Language switching
5. ✅ FAQ responses
6. ✅ Escalation triggers
7. ✅ Mobile responsiveness

---

## Troubleshooting

### Common Issues

**API Key errors:**
```bash
# Check if environment variable is set
echo $OPENAI_API_KEY
```

**Port conflicts:**
```bash
# Change default port
streamlit run app.py --server.port=8080
```

**Module not found:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Voice not working:**
- Voice features require browser microphone permissions
- Check browser compatibility
- Microphone not available on all deployment platforms

---

## Cost Estimation

### Streamlit Cloud
- Free tier: 1 app, limited resources
- Paid: $20-100/month

### Heroku
- Free tier: Available (with limitations)
- Hobby: $7/month
- Standard: $25-50/month

### AWS EC2
- t2.micro: Free tier (12 months)
- t2.medium: ~$30/month

### Azure/GCP
- Similar pricing to AWS
- Free credits available for new accounts

### OpenAI API Costs
- GPT-4: ~$0.03 per 1K tokens
- Estimate: $10-100/month depending on usage

---

## Support & Updates

For issues or questions:
- Check GitHub issues
- Review logs
- Contact support

Keep dependencies updated:
```bash
pip install --upgrade -r requirements.txt
```

---

## Next Steps

After deployment:
1. Share the URL with your team
2. Monitor usage and performance
3. Collect user feedback
4. Iterate and improve
5. Scale as needed

Good luck with your deployment! 🚀
