#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Log file for debugging
LOG_FILE="setup.log"

# Clear previous log
> "$LOG_FILE"

# Spinner Animation Function
spinner() {
    local pid=$1
    local text=$2
    local spin='-\|/'
    local i=0
    local start_time=$(date +%s)

    # Hide cursor
    tput civis

    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) %4 ))
        # Dynamic time counter
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))
        
        printf "\r${CYAN}[${spin:$i:1}]${NC} %s ${YELLOW}(${elapsed}s)${NC}" "$text"
        sleep 0.1
    done

    # Restore cursor
    tput cnorm

    wait $pid
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        printf "\r${GREEN}[✔]${NC} %-50s\n" "$text"
    else
        printf "\r${RED}[✘]${NC} %-50s\n" "$text"
        echo -e "${RED}[!] Error occurred. Check $LOG_FILE for details.${NC}"
        exit 1
    fi
}

# Enhanced OS detection
detect_os() {
    if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux/files" ]; then
        echo "Termux"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "MacOS"
    else
        echo "Unknown"
    fi
}

# Display banner
show_banner() {
    if [ -f "banner/banner.txt" ]; then
        echo -e "${GREEN}"
        cat "banner/banner.txt"
        echo -e "${NC}"
    else
        # Fallback mini banner
        echo -e "${GREEN}SCARFACE SETUP${NC}"
    fi
}

# Helper functions
info() { echo -e "${CYAN}[*]${NC} $1"; }

# Create launcher script
create_launcher() {
    local launcher_path="$PWD/.launcher"
    
    # Run in background to use spinner
    (
        cat > "$launcher_path" <<EOL
#!/bin/bash
# Wrapper script for Scarface phishing tool

cd "$PWD"
CLEAR='cls' && [[ \$OSTYPE == linux* || \$OSTYPE == darwin* ]] && CLEAR='clear'
python3 main.py "\$@"
EOL
        chmod +x "$launcher_path"
    ) >> "$LOG_FILE" 2>&1 &
    
    spinner $! "Configuring launcher script"
}

# Install dependencies based on OS
install_dependencies() {
    local os="$1"
    
    # 1. System Level Python Installation
    if ! command -v python3 &>/dev/null; then
        info "Python not found. Initializing installer..."
        case "$os" in
            Termux)
                (pkg update -y && pkg install -y python) >> "$LOG_FILE" 2>&1 &
                spinner $! "Installing Python (Termux)"
                ;;
            Linux)
                # Pre-validate sudo to avoid background hang
                sudo -v
                (sudo apt update && sudo apt install -y python3 python3-pip) >> "$LOG_FILE" 2>&1 &
                spinner $! "Installing Python (APT)"
                ;;
            MacOS)
                if ! command -v brew &>/dev/null; then
                    echo -e "${RED}[-] Homebrew required.${NC}"
                    exit 1
                fi
                (brew install python) >> "$LOG_FILE" 2>&1 &
                spinner $! "Installing Python (Homebrew)"
                ;;
            *)
                echo -e "${RED}[-] Manual installation required.${NC}"
                exit 1
                ;;
        esac
    else
        echo -e "${GREEN}[✔]${NC} Python is already installed"
    fi

    # 2. PIP Installation
    if ! command -v pip3 &>/dev/null; then
        case "$os" in
            Termux) 
                (python -m ensurepip) >> "$LOG_FILE" 2>&1 & 
                spinner $! "Bootstrapping pip"
                ;;
            *)      
                (sudo python3 -m ensurepip) >> "$LOG_FILE" 2>&1 & 
                spinner $! "Bootstrapping pip"
                ;;
        esac
    fi

    # 3. Python Requirements
    if [ -f "requirements.txt" ]; then
        # We run pip with --user or normal depending on env, hiding output
        (pip3 install -r requirements.txt) >> "$LOG_FILE" 2>&1 &
        spinner $! "Installing Python dependencies"
    else
        echo -e "${YELLOW}[!]${NC} No requirements.txt found"
    fi
}

# Create global symlink
create_symlink() {
    local os="$1"
    local install_path
    local use_sudo=0
    
    case "$os" in
        Termux) 
            install_path="/data/data/com.termux/files/usr/bin" 
            ;;
        Linux|MacOS) 
            install_path="/usr/local/bin"
            use_sudo=1
            ;;
        *) return ;;
    esac

    local launcher_path="$PWD/.launcher"
    
    # Create launcher if missing
    [ ! -f "$launcher_path" ] && create_launcher

    # Perform Symlink logic in background block
    (
        cmd_prefix=""
        [ "$use_sudo" -eq 1 ] && cmd_prefix="sudo"
        
        if [ -L "$install_path/phish" ]; then
            $cmd_prefix rm "$install_path/phish"
        fi
        $cmd_prefix ln -sf "$launcher_path" "$install_path/phish"
    ) >> "$LOG_FILE" 2>&1 &

    spinner $! "Creating system shortcut 'phish'"
}

# Main setup routine
main() {
    # Clear screen for fresh start
    clear
    show_banner
    
    if [ ! -f "main.py" ]; then
        echo -e "${RED}[-] Run this script from Scarface project root!${NC}"
        exit 1
    fi

    local os=$(detect_os)
    echo -e "${CYAN}[*]${NC} Target System: ${YELLOW}$os${NC}\n"
    
    create_launcher
    install_dependencies "$os"
    create_symlink "$os"
    
    echo -e "\n${GREEN}Setup Completed Successfully!${NC}"
    echo -e "${CYAN}[*]${NC} Logs saved to: ${YELLOW}./$LOG_FILE${NC}"
    echo -e "${CYAN}[*]${NC} Type ${GREEN}phish${NC} to launch Scarface."
}

main
