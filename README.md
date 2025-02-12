# Telegram Bot

A Telegram bot with product catalog and order management.

## Local Development Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd <repo-directory>
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your bot token:
```
TELEGRAM_TOKEN=your_bot_token_here
```

5. Run the bot:
```bash
python bot.py
```

## VPS Deployment

### Initial Setup

1. SSH into your VPS:
```bash
ssh user@your-vps-ip
```

2. Install required packages:
```bash
sudo apt update
sudo apt install python3 python3-venv git
```

3. Clone the repository:
```bash
git clone <your-repo-url>
cd <repo-directory>
```

4. Make the setup script executable:
```bash
chmod +x setup.sh
```

5. Run the setup script:
```bash
./setup.sh
```

The script will:
- Create .env file (if not exists) and prompt for your bot token
- Set up Python virtual environment
- Install dependencies
- Create and configure systemd service
- Start the bot service

### Updating the Bot

To update the bot with latest changes:

1. Push your changes to GitHub from your local machine
2. On the VPS, run the setup script again:
```bash
./setup.sh
```

The script will:
- Pull latest changes from GitHub
- Update dependencies if needed
- Restart the bot service automatically

### Monitoring

- Check bot status:
```bash
sudo systemctl status telegrambot
```

- View logs:
```bash
sudo journalctl -u telegrambot -f
```

### Security Notes

1. The `.env` file containing your bot token is excluded from git
2. The systemd service runs under a dedicated user
3. The bot automatically restarts if it crashes
4. All sensitive data is kept on the VPS only

## Deploy to Production (Free Options)

### Option 1: Deploy on PythonAnywhere (Recommended for Beginners)
1. Create a free account on [PythonAnywhere](https://www.pythonanywhere.com)
2. Upload your files (bot.py, requirements.txt, .env)
3. Open a bash console and run:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Go to the "Web" tab and set up a new web app
5. Set up an "Always-on task" to run your bot
6. Start your bot with: `python bot.py`

### Option 2: Deploy on Render
1. Create a free account on [Render](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
5. Add your environment variables in the Render dashboard

### Option 3: Deploy on Railway
1. Create an account on [Railway](https://railway.app)
2. Create a new project
3. Connect your GitHub repository
4. Add your environment variables
5. Deploy automatically

## Basic Bot Commands
- `/start` - Start the bot
- `/help` - Get help message
- Send any text message to get an echo response

## Notes
- The free tier of these platforms should be sufficient for basic bot functionality
- Keep your bot token secret and never commit it to version control
- The bot will run as long as your script is running 