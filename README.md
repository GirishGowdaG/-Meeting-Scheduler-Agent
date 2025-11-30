# SmartMeet — AI Meeting Scheduler

An intelligent meeting scheduling application that integrates with Google Calendar to help you manage your schedule efficiently. SmartMeet provides a visual calendar interface, availability checking, and automated meeting creation with Google Meet integration.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Limitations](#️-limitations)
- [Tech Stack](#️-tech-stack)
- [Architecture](#️-architecture)
- [Setup & Run Instructions](#-setup--run-instructions)
- [Environment Variables](#environment-variables)
- [Google OAuth Setup](#google-oauth-setup)
- [API Endpoints](#api-endpoints)
- [Screenshots & Demo](#-screenshots--demo)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Potential Improvements](#-potential-improvements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📖 Overview

SmartMeet is a full-stack web application designed to simplify meeting scheduling by:
- **Visualizing your availability** in an intuitive hourly calendar view (9 AM - 6 PM)
- **Checking Google Calendar** for conflicts and free time slots
- **Automatically creating meetings** with Google Meet links and email invitations
- **Managing your schedule** with today's schedule view and meeting history
- **Supporting partial availability** - book meetings in free time within busy hours

The application uses Google OAuth for authentication and integrates directly with Google Calendar API to provide real-time availability and seamless meeting creation.

---

## ✨ Features

### Core Features:
- 🔐 **Google OAuth Authentication** - Secure login with your Google account
- 📅 **Visual Calendar Interface** - See your availability at a glance (9 AM - 6 PM)
- 🟢 **Smart Availability Detection** - Color-coded slots (Green=Free, Yellow=Partial, Red=Busy)
- ⏰ **Partial Availability** - Book meetings in free time within busy hours
- 📧 **Automatic Invitations** - Send calendar invites to all participants
- 🎥 **Google Meet Integration** - Automatic video conference links
- 📊 **Meeting History** - Track upcoming and completed meetings
- 🗓️ **Today's Schedule** - View daily schedule for any date
- 🗑️ **Meeting Management** - Delete meetings from calendar and database
- 🌍 **Timezone Support** - GMT+5:30 (Asia/Kolkata) with proper conversion

### User Interface:
- **Schedule Page** - Create new meetings with form-based input
- **History Page** - View upcoming and completed meetings in separate tabs
- **Today's Schedule** - See all meetings for any selected day
- **Event Details Modal** - View meeting information by clicking busy slots
- **Responsive Design** - Works on desktop and mobile devices

### Feature Comparison:

| Feature | SmartMeet | Google Calendar | Calendly |
|---------|-----------|-----------------|----------|
| Visual Availability | ✅ | ✅ | ✅ |
| Google Calendar Sync | ✅ | ✅ | ✅ |
| Partial Availability | ✅ | ❌ | ❌ |
| Meeting History | ✅ | ✅ | ✅ |
| Today's Schedule | ✅ | ✅ | ❌ |
| Auto Google Meet | ✅ | ✅ | ✅ |
| Collaborative Booking | ❌ | ❌ | ✅ |
| Recurring Meetings | ❌ | ✅ | ✅ |
| Multiple Calendars | ❌ | ✅ | ✅ |
| Mobile App | ❌ | ✅ | ✅ |
| Free to Use | ✅ | ✅ | Limited |

---

## ⚠️ Limitations

### Current Limitations:
- **Single User Focus** - Designed for individual use, not team collaboration
- **No Recurring Meetings** - Each meeting must be created separately
- **Limited Timezone Support** - Currently optimized for GMT+5:30 (Asia/Kolkata)
- **No Room Booking** - Does not handle conference room or resource scheduling
- **Participant Availability** - Cannot check other participants' calendars (assumes working hours)
- **No Mobile App** - Web-only interface (responsive but not native mobile)
- **SQLite Database** - Not suitable for high-traffic production use
- **No Offline Mode** - Requires internet connection for all operations
- **Basic AI Integration** - Intent extraction is mock implementation (Gemini AI optional)

### Known Issues:
- Timezone conversion may need adjustment for users outside GMT+5:30
- Large number of meetings may slow down history page
- No conflict resolution for overlapping meeting requests

---

---

## 🚀 Setup & Run Instructions

### Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.10 or higher** - [Download](https://www.python.org/downloads/)
- **Node.js 18 or higher** - [Download](https://nodejs.org/)
- **Git** (optional) - For cloning the repository

### Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+
- Node.js 20+
- Google Cloud account
- Anthropic API key

### Option 1: Automated Setup (Easiest - Windows)

**Using Batch Scripts:**

1. **First Time Setup:**
   ```bash
   # Install Python 3.10+ and Node.js 18+ first
   
   # Setup backend
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python scripts/init_db.py
   
   # Setup frontend
   cd frontend
   npm install
   ```

2. **Configure Google OAuth** (see section below)

3. **Start Application:**
   - Double-click `START.bat` (starts both backend and frontend)
   - Or run: `python setup_and_run.py`

4. **Stop Application:**
   - Double-click `STOP.bat`

### Option 2: Manual Setup (All Platforms)

### 2. Configure Credentials

Before first run, you need:

**A. Google OAuth Setup** (2 minutes)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable "Google Calendar API"
3. Create OAuth 2.0 Client ID
4. Add redirect URI: `http://localhost:8000/auth/google/callback`
5. Copy Client ID and Secret

**B. Get Anthropic API Key** (1 minute)
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create API key

**C. Update Configuration**
```bash
# Edit backend/.env with your credentials
cd backend
python scripts/generate_keys.py  # Generate SECRET_KEY and ENCRYPTION_KEY
# Add all keys to .env file
```

### 3. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🛠️ Tech Stack

### Frontend:
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with Tailwind
- **Date Handling**: date-fns
- **HTTP Client**: Axios
- **Routing**: Next.js App Router

### Backend:
- **Framework**: FastAPI (Python 3.10+)
- **ORM**: SQLAlchemy
- **Database Migrations**: Alembic
- **Authentication**: JWT tokens
- **Encryption**: Cryptography library (Fernet)
- **API Documentation**: Swagger/OpenAPI (auto-generated)

### Database:
- **Development**: SQLite
- **Production Ready**: PostgreSQL (recommended)
- **Schema**: Users, AuthTokens, Meetings

### APIs & Services:
- **Google Calendar API v3** - Calendar integration and event management
  - `events.list` - Fetch events in time range
  - `events.insert` - Create new calendar events
  - `events.delete` - Remove calendar events
  - `freebusy.query` - Check availability
- **Google OAuth 2.0 API** - User authentication and authorization
  - OAuth flow for secure login
  - Token refresh mechanism
  - Scope: calendar.events, calendar.readonly, userinfo
- **Google Meet API** - Automatic video conference link generation
  - Conference data creation
  - Meet link embedding in events
- **Gemini AI API** (Optional) - Natural language intent extraction
  - Parse meeting requests
  - Extract date, time, duration, participants

### Development Tools:
- **Package Managers**: npm (frontend), pip (backend)
- **Environment**: Python virtual environment (.venv)
- **Hot Reload**: Uvicorn (backend), Next.js dev server (frontend)

---

## Local Setup (Development)

### 1. Clone Repository

```bash
git clone <repo-url>
cd smartmeet
```

### 2. Backend Setup (FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env and set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ANTHROPIC_API_KEY, etc.

# Run database migrations (creates tables)
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Start backend server
uvicorn main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local if needed (default: NEXT_PUBLIC_API_URL=http://localhost:8000)

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

---

## Environment Variables

### Backend (.env)

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Anthropic API
ANTHROPIC_API_KEY=your-anthropic-api-key

# Application
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./smartmeet.db
ENCRYPTION_KEY=your-32-byte-encryption-key-base64-encoded

# CORS
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
```

**Generate SECRET_KEY and ENCRYPTION_KEY:**
```bash
cd backend
python scripts/generate_keys.py
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Calendar API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure OAuth consent screen
6. Add authorized redirect URI: `http://localhost:8000/auth/google/callback`
7. Copy Client ID and Client Secret to backend `.env`

---

## API Endpoints

- `GET /auth/google/login` — Start OAuth flow
- `GET /auth/google/callback` — OAuth callback
- `POST /api/parse-intent` — Parse natural language into JSON
- `POST /api/propose-slots` — Propose candidate slots
- `POST /api/create-event` — Create Google Calendar event
- `GET /api/meetings/history` — List user meetings

---

## 🏗️ Architecture

### System Architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Schedule   │  │   History    │  │   Today's    │     │
│  │     Page     │  │     Page     │  │   Schedule   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                          │                                   │
│                    API Client (Axios)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST
┌──────────────────────────┴──────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Auth       │  │  Scheduling  │  │   Meetings   │     │
│  │   Routes     │  │    Routes    │  │    Routes    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│  ┌──────┴──────────────────┴──────────────────┴───────┐    │
│  │              Services Layer                         │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────┐ │    │
│  │  │   Google    │  │   Meeting    │  │   JWT    │ │    │
│  │  │  Calendar   │  │   Service    │  │  Utils   │ │    │
│  │  └─────────────┘  └──────────────┘  └──────────┘ │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                    SQLAlchemy ORM                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                   SQLite Database                            │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Users   │  │  AuthTokens  │  │   Meetings   │         │
│  └──────────┘  └──────────────┘  └──────────────┘         │
└──────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                   External APIs                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  Google Calendar │  │   Google OAuth   │                │
│  │       API        │  │       2.0        │                │
│  └──────────────────┘  └──────────────────┘                │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow:

1. **Authentication Flow:**
   - User clicks "Login with Google"
   - Redirected to Google OAuth consent screen
   - Google returns authorization code
   - Backend exchanges code for access/refresh tokens
   - Tokens encrypted and stored in database
   - JWT token issued to frontend

2. **Meeting Creation Flow:**
   - User fills meeting form (title, date, duration, participants)
   - Frontend requests day availability from backend
   - Backend queries Google Calendar API for busy/free status
   - Frontend displays color-coded hourly slots
   - User selects available slot
   - Backend creates event via Google Calendar API
   - Event details stored in local database
   - Calendar invites sent to participants

3. **Availability Check Flow:**
   - Frontend requests availability for specific date
   - Backend fetches events from Google Calendar (9 AM - 6 PM)
   - Backend calculates busy/free/partial status for each hour
   - Backend identifies free periods within busy hours
   - Frontend displays visual calendar with color coding

---

## 🧪 Testing

### Manual Testing:
- Use test Google accounts for OAuth testing
- Test with various meeting durations (15, 30, 60 minutes)
- Test partial availability by creating overlapping events
- Test timezone handling with different calendar settings

### Automated Testing:
- Unit tests located in `backend/tests/`
- Run tests: `pytest backend/tests/`
- Property-based tests use Hypothesis framework (100+ iterations)

### Test Scenarios:
1. Create meeting in free slot → Should succeed
2. Create meeting in busy slot → Should show as busy
3. Create meeting in partial slot → Should show free periods
4. Delete meeting → Should remove from calendar and database
5. View history → Should show upcoming and completed separately

---

## 🐛 Troubleshooting

### Common Issues:

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
cd backend
pip install -r requirements.txt

# Check if port 8000 is in use
netstat -ano | findstr :8000
```

**Frontend won't start:**
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
cd frontend
rm -rf node_modules .next
npm install
```

**Google OAuth errors:**
- Verify credentials in `backend/.env`
- Check redirect URI matches exactly: `http://localhost:3000/auth/callback`
- Ensure Google Calendar API is enabled in Google Cloud Console
- Check OAuth consent screen is configured

**Database errors:**
```bash
# Reinitialize database
cd backend
rm smartmeet.db
python scripts/init_db.py
```

**Port already in use:**
```bash
# Windows - Kill processes
taskkill /F /IM node.exe
taskkill /F /IM python.exe

# Or use STOP.bat
```

**Calendar not syncing:**
- Check internet connection
- Verify Google Calendar API quota not exceeded
- Check access token is valid (may need to re-login)
- Verify timezone settings in backend

### Getting Help:
- Check `HOW_TO_RUN.md` for detailed instructions
- Review `QUICK_START.md` for quick reference
- Check backend logs for error messages
- Check browser console (F12) for frontend errors

---

---

## 🚀 Potential Improvements

### High Priority:
1. **Collaborative Scheduling**
   - Allow users to see friends' availability
   - Enable mutual booking between users
   - Friend management system
   - Shareable booking links (like Calendly)

2. **Enhanced Timezone Support**
   - Automatic timezone detection
   - Support for multiple timezones
   - Timezone conversion for participants in different zones

3. **Recurring Meetings**
   - Daily, weekly, monthly recurring patterns
   - Custom recurrence rules
   - Bulk management of recurring events

4. **Advanced AI Features**
   - Full Gemini AI integration for natural language processing
   - Voice input for meeting creation
   - Smart meeting suggestions based on patterns
   - Automatic meeting title and description generation

### Medium Priority:
5. **Email Notifications**
   - Custom email templates
   - Meeting reminders (15 min, 1 hour, 1 day before)
   - Confirmation emails
   - Cancellation notifications

6. **Calendar Enhancements**
   - Multiple calendar views (day, week, month)
   - Drag-and-drop rescheduling
   - Custom working hours per day
   - Buffer time between meetings

7. **Team Features**
   - Team calendars
   - Room/resource booking
   - Participant availability checking
   - Group meeting scheduling

8. **Mobile Experience**
   - Native mobile apps (iOS/Android)
   - Progressive Web App (PWA)
   - Mobile-optimized interface
   - Push notifications

### Low Priority:
9. **Analytics & Insights**
   - Meeting statistics
   - Time spent in meetings
   - Most frequent participants
   - Productivity insights

10. **Integrations**
    - Slack integration
    - Microsoft Teams
    - Zoom integration
    - Outlook Calendar support

11. **Customization**
    - Custom themes
    - Personalized booking pages
    - Custom availability rules
    - Meeting templates

12. **Performance & Scalability**
    - PostgreSQL migration
    - Redis caching
    - API rate limiting
    - Load balancing
    - CDN for static assets

### Technical Improvements:
- **Testing**: Unit tests, integration tests, E2E tests
- **CI/CD**: Automated deployment pipeline
- **Monitoring**: Error tracking, performance monitoring
- **Security**: Enhanced encryption, audit logs
- **Documentation**: API documentation, user guides

---

## 📸 Screenshots & Demo

### Main Features:

1. **Login Page** - Google OAuth authentication
2. **Schedule Page** - Create meetings with visual calendar
3. **Availability View** - Color-coded hourly slots (9 AM - 6 PM)
4. **Event Details** - Click busy slots to see meeting information
5. **Meeting History** - Upcoming and completed meetings
6. **Today's Schedule** - Daily schedule view for any date

### Demo Flow (2-3 Minutes):

1. Open http://localhost:3000
2. Click **"Login with Google"** → Authenticate
3. Fill meeting form:
   - Title: "Team Sync"
   - Date: Tomorrow
   - Duration: 30 minutes
   - Participants: alice@example.com
4. Click **"Check Availability"**
5. View color-coded slots (Green/Yellow/Red)
6. Click available slot → Click **"Create Meeting"**
7. Success! Event created in Google Calendar
8. Navigate to **"History"** to see scheduled meeting
9. Navigate to **"Today's Schedule"** to view daily agenda

---

---

## 📊 Project Statistics

- **Lines of Code**: ~5,000+ (Backend: ~2,500, Frontend: ~2,500)
- **Files**: 50+ source files
- **API Endpoints**: 10+ REST endpoints
- **Database Tables**: 3 (Users, AuthTokens, Meetings)
- **Pages**: 4 (Login, Schedule, History, Today's Schedule)
- **Development Time**: ~40 hours
- **Dependencies**: 30+ npm packages, 20+ Python packages

---

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome!

### How to Contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Areas for Contribution:
- Bug fixes
- UI/UX improvements
- Additional features from "Potential Improvements"
- Documentation improvements
- Test coverage

---

## 📄 License

MIT License - Feel free to use this project for learning and personal use.

---

## 👨‍💻 Author

Built with ❤️ using:
- **Kiro AI** - AI-powered development assistant
- **Claude Sonnet 4.5** - Spec-driven scaffolding
- **Next.js** - React framework
- **FastAPI** - Python web framework
- **Google Calendar API** - Calendar integration

---

## 🙏 Acknowledgments

- Google Calendar API for calendar integration
- Next.js team for the amazing React framework
- FastAPI team for the fast Python web framework
- Tailwind CSS for beautiful styling
- The open-source community

---

## 📞 Support

For issues, questions, or suggestions:
- Check the documentation files (HOW_TO_RUN.md, QUICK_START.md)
- Review the troubleshooting section above
- Check existing issues in the repository

---

## 🎯 Project Status

**Status**: ✅ **Production Ready** (for personal use)

**Last Updated**: November 2025

**Version**: 1.0.0

---

**⭐ If you find this project useful, please consider giving it a star!**
