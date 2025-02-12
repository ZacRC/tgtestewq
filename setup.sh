#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting bot setup/update process...${NC}"

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo -e "${YELLOW}Creating data directory...${NC}"
    mkdir -p data
fi

# Check if .env exists, if not create it
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating one...${NC}"
    read -p "Enter your Telegram Bot Token: " token
    echo "TELEGRAM_TOKEN=$token" > .env
    echo -e "${GREEN}.env file created successfully!${NC}"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created!${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Backup existing data if exists
echo -e "${YELLOW}Backing up existing data...${NC}"
if [ -f "data/orders.json" ]; then
    cp data/orders.json data/orders.json.backup
fi
if [ -f "data/carts.json" ]; then
    cp data/carts.json data/carts.json.backup
fi

# Pull latest changes from git
echo -e "${YELLOW}Pulling latest changes from repository...${NC}"
git pull origin main

# Install/Update dependencies
echo -e "${YELLOW}Installing/Updating dependencies...${NC}"
pip install -r requirements.txt

# Check if the bot is already running
if pgrep -f "python3 bot.py" > /dev/null; then
    echo -e "${YELLOW}Stopping existing bot process...${NC}"
    pkill -f "python3 bot.py"
    sleep 2
fi

# Create systemd service file if it doesn't exist
if [ ! -f "/etc/systemd/system/telegrambot.service" ]; then
    echo -e "${YELLOW}Creating systemd service...${NC}"
    sudo tee /etc/systemd/system/telegrambot.service > /dev/null << EOL
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin:$PATH
ExecStart=$(pwd)/venv/bin/python3 bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

    # Enable the service
    sudo systemctl enable telegrambot.service
    echo -e "${GREEN}Systemd service created and enabled!${NC}"
fi

# Restore data backups if they exist
echo -e "${YELLOW}Restoring data from backups...${NC}"
if [ -f "data/orders.json.backup" ]; then
    mv data/orders.json.backup data/orders.json
fi
if [ -f "data/carts.json.backup" ]; then
    mv data/carts.json.backup data/carts.json
fi

# Restart the service
echo -e "${YELLOW}Starting/Restarting the bot...${NC}"
sudo systemctl restart telegrambot.service
sleep 2

# Check service status
if systemctl is-active --quiet telegrambot.service; then
    echo -e "${GREEN}Bot is running successfully!${NC}"
    echo -e "\nYou can check the bot status with: ${YELLOW}sudo systemctl status telegrambot${NC}"
    echo -e "View logs with: ${YELLOW}sudo journalctl -u telegrambot -f${NC}"
else
    echo -e "${RED}Failed to start the bot. Check logs with: sudo journalctl -u telegrambot -f${NC}"
fi 