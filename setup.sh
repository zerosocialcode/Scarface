#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

INSTALL_DIR="/usr/local/bin"
TERMUX_DIR="/data/data/com.termux/files/usr/bin"

# Clear screen
clear

# --- DISPLAY BANNER ---
BANNER_FILE="assets/banners/setup.txt"
if [ -f "$BANNER_FILE" ]; then
    echo -e "${CYAN}"
    cat "$BANNER_FILE"
    echo -e "${NC}"
fi

echo -e "${CYAN}   Scarface Framework Installer${NC}"
echo "----------------------------------------"

# Detect environment
if [ -d "$TERMUX_DIR" ]; then
    echo -e "${GREEN}[+] Termux environment detected.${NC}"
    INSTALL_DIR="$TERMUX_DIR"
    PKG_MGR="pkg"
    SUDO=""
else
    echo -e "${GREEN}[+] Linux/MacOS environment detected.${NC}"
    SUDO="sudo"
    
    # Check for sudo permission if not root
    if [ "$EUID" -ne 0 ]; then
        echo -e "${CYAN}[*] Requesting sudo privileges...${NC}"
        sudo -v
    fi
fi

# 1. Install Dependencies
echo -e "${CYAN}[*] Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --break-system-packages > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✔] Dependencies installed successfully.${NC}"
    else
        # Fallback
        pip3 install -r requirements.txt > /dev/null 2>&1
        echo -e "${GREEN}[✔] Dependencies installed.${NC}"
    fi
else
    echo -e "${RED}[!] requirements.txt not found!${NC}"
    exit 1
fi

# 2. Create Global Executable
echo -e "${CYAN}[*] Configuring global command 'scarface'...${NC}"

# Get absolute path of the current directory
PROJECT_DIR=$(pwd)
CONSOLE_SCRIPT="$PROJECT_DIR/src/console.py"

# Create the wrapper script content
WRAPPER="#!/bin/bash
python3 \"$CONSOLE_SCRIPT\" \"\$@\"
"

# Write to temporary file then move
echo "$WRAPPER" > scarface_tmp
chmod +x scarface_tmp

# Move to bin folder
$SUDO mv scarface_tmp "$INSTALL_DIR/scarface"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[✔] Successfully installed!${NC}"
    echo -e "\nYou can now run the tool by typing: ${GREEN}scarface${NC}"
else
    echo -e "${RED}[!] Failed to install global command.${NC}"
    echo "Check permissions or try running as root."
fi
