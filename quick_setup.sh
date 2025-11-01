#!/bin/bash
# Quick Setup Script for News Hack Bot
# Run this after cloning the repository

echo "🔐 News Hack Bot - Quick Setup"
echo "================================"
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to reconfigure? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing configuration."
        exit 0
    fi
fi

# Get bot token
echo "📱 Telegram Bot Configuration"
echo "------------------------------"
echo ""
read -p "Enter your Telegram Bot Token: " BOT_TOKEN

# Get chat ID
echo ""
read -p "Enter your Telegram Chat ID: " CHAT_ID

# Get check interval
echo ""
read -p "RSS check interval in minutes (default: 30): " CHECK_INTERVAL
CHECK_INTERVAL=${CHECK_INTERVAL:-30}

# Create .env file
cat > .env << EOF
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=${BOT_TOKEN}
TELEGRAM_CHAT_ID=${CHAT_ID}

# RSS Feed Check Interval (in minutes)
CHECK_INTERVAL=${CHECK_INTERVAL}

# Database Path
DATABASE_PATH=./data/news.db

# Logging Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
EOF

echo ""
echo "✅ Configuration saved to .env"
echo ""
echo "Next steps:"
echo "1. Run: ./install.sh"
echo "2. Test: ./venv/bin/python3 main.py"
echo "3. Install systemd service (see INSTALL_GUIDE.md)"
echo ""
