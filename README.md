# Snap & Study 📚🤖

Snap & Study is an AI-powered study assistant that helps students understand
problems, diagrams, notes, and textbook pages using Gemini AI.

## Features

- 📸 Upload study problems, diagrams, or notes
- 🤖 AI-powered explanations using Gemini
- 📝 Step-by-step solutions
- 💬 Ask study questions directly
- 📱 Send study summaries to WhatsApp using Twilio

## Technologies

- Python
- Streamlit
- Google Gemini AI
- Twilio WhatsApp

## Setup

### 1. Clone the repository

git clone https://github.com/Pranav-Sandbhor-008/snap-and-study.git

cd snap-and-study

### 2. Create a virtual environment

python -m venv venv

### 3. Activate the environment

Windows PowerShell:

venv\Scripts\Activate.ps1

### 4. Install dependencies

pip install -r requirements.txt

### 5. Configure API keys

Create:

.streamlit/secrets.toml

Add:

GEMINI_API_KEY = "your-gemini-api-key"
TWILIO_ACCOUNT_SID = "your-twilio-account-sid"
TWILIO_AUTH_TOKEN = "your-twilio-auth-token"
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
TWILIO_CONTENT_SID = "your-content-template-sid"

### 6. Run the application

streamlit run app.py
