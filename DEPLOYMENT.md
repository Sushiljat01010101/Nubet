# Render.com Deployment Guide

## 🚀 Deploy Pirate OSINT Bot on Render

### Step 1: Prepare Your Repository
1. Push your code to GitHub/GitLab
2. Make sure all files are committed:
   - `main.py`
   - `bot_handlers.py` 
   - `config.py`
   - `osint_api.py`
   - `utils.py`
   - `render.yaml`
   - `dependencies.txt`

### Step 2: Create Render Service
1. Go to [render.com](https://render.com)
2. Connect your GitHub/GitLab account
3. Click "New +" → "Web Service"
4. Select your repository

### Step 3: Configure Deployment
**Build & Deploy Settings:**
- **Environment:** Python 3
- **Build Command:** `pip install pyTelegramBotAPI requests python-dotenv`
- **Start Command:** `python main.py`

### Step 4: Set Environment Variables
Add these environment variables in Render dashboard:

**Required:**
- `TELEGRAM_BOT_TOKEN` = Your bot token from @BotFather

**Optional (already configured):**
- `PIRATE_OSINT_API_KEY` = kQ5hlafjxfgJTJ5d
- `PIRATE_OSINT_BASE_URL` = http://pirate-osint.onrender.com/api
- `RATE_LIMIT_REQUESTS` = 5
- `RATE_LIMIT_WINDOW` = 60
- `LOG_LEVEL` = INFO
- `API_TIMEOUT` = 30

### Step 5: Deploy
1. Click "Create Web Service"
2. Render will automatically build and deploy
3. Your bot will be live in 2-3 minutes!

### 🔧 Alternative Manual Setup

If render.yaml doesn't work, use these settings:

**Runtime:** Python 3
**Build Command:** 
```bash
pip install pyTelegramBotAPI requests python-dotenv
```

**Start Command:** 
```bash
python main.py
```

### 📱 Verify Deployment
1. Check Render logs for "Bot initialized successfully"
2. Test your bot on Telegram with /start
3. Try a phone number lookup

### 🎯 Your Bot Features
- ✅ Interactive button interface
- ✅ Professional OSINT results formatting  
- ✅ Rate limiting and error handling
- ✅ Multiple phone number format support
- ✅ Real-time status monitoring

**Bot is ready for production use!** 🎉