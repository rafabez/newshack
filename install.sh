#!/bin/bash
# Installation script for News Hack Bot

set -e

echo "=========================================="
echo "News Hack Bot - Installation Script"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run this script as root${NC}"
    exit 1
fi

# Get current user and directory
CURRENT_USER=$(whoami)
INSTALL_DIR=$(pwd)

echo -e "${GREEN}Installing for user: ${CURRENT_USER}${NC}"
echo -e "${GREEN}Installation directory: ${INSTALL_DIR}${NC}"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed!${NC}"
    echo "Install it with: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p data logs
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Setup .env file
echo "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env file with your configuration${NC}"
    echo -e "${YELLOW}  Required: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID${NC}"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi
echo ""

# Setup systemd service
echo "Setting up systemd service..."
SERVICE_FILE="newshack.service"
SYSTEMD_SERVICE="/etc/systemd/system/newshack.service"

# Replace placeholders in service file
sed "s|YOUR_USERNAME|${CURRENT_USER}|g" ${SERVICE_FILE} > ${SERVICE_FILE}.tmp
sed -i "s|/home/YOUR_USERNAME/newshack|${INSTALL_DIR}|g" ${SERVICE_FILE}.tmp

echo -e "${YELLOW}To install the systemd service, run:${NC}"
echo ""
echo "  sudo cp ${SERVICE_FILE}.tmp ${SYSTEMD_SERVICE}"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable newshack"
echo "  sudo systemctl start newshack"
echo ""

# Make main.py executable
chmod +x main.py

echo "=========================================="
echo -e "${GREEN}Installation completed!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your bot token and chat ID"
echo "2. Test the bot: ./venv/bin/python3 main.py"
echo "3. Install systemd service (commands above)"
echo "4. Check status: sudo systemctl status newshack"
echo "5. View logs: tail -f logs/newshack.log"
echo ""
echo "Bot commands:"
echo "  /start - Show welcome message"
echo "  /news - Get latest news"
echo "  /recent - Recent 24h news"
echo "  /stats - Bot statistics"
echo "  /feeds - Feed status"
echo "  /categories - Browse by category"
echo "  /search [term] - Search news"
echo "  /update - Force feed update"
echo ""
echo -e "${GREEN}Happy hacking! 🔐${NC}"
