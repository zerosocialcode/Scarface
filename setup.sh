#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

# Display banner if available
show_banner() {
    if [ -f "banner/banner.txt" ]; then
        echo -e "${GREEN}"
        cat "banner/banner.txt"
        echo -e "${NC}"
    fi
}

# Colorful message functions
info() { echo -e "${CYAN}[*]${NC} $1"; }
success() { echo -e "${GREEN}[+]${NC} $1"; }
warning() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[-]${NC} $1"; }

# Create launcher script
create_launcher() {
    local launcher_path="$PWD/.launcher"
    
    if [ -f "$launcher_path" ]; then
        info "Updating existing launcher script..."
    else
        info "Creating launcher script..."
    fi

    # Create launcher script with banner support
    cat > "$launcher_path" <<EOL
#!/bin/bash
# Wrapper script for Scarface phishing tool

# Change to script directory
cd "$PWD"

# Set clear command based on OS
CLEAR='cls' && [[ \$OSTYPE == linux* || \$OSTYPE == darwin* ]] && CLEAR='clear'


# Execute main script
python3 main.py "\$@"
EOL

    # Make launcher executable
    chmod +x "$launcher_path"
    success "Launcher script created: ${GREEN}.launcher${NC}"
}

# Install dependencies based on OS
install_dependencies() {
    local os="$1"
    
    # Check for Python
    if ! command -v python3 &>/dev/null; then
        warning "Python not found. Installing..."
        case "$os" in
            Termux)
                info "Updating Termux packages..."
                pkg update -y && pkg install -y python
                ;;
            Linux)
                info "Updating package lists..."
                sudo apt update && sudo apt install -y python3 python3-pip
                ;;
            MacOS)
                if ! command -v brew &>/dev/null; then
                    error "Homebrew required. Install from: ${CYAN}https://brew.sh${NC}"
                    exit 1
                fi
                info "Installing Python via Homebrew..."
                brew install python
                ;;
            *)
                error "Unsupported OS. Manual Python installation required."
                exit 1
                ;;
        esac
        success "Python installed successfully!"
    else
        info "Python is already installed"
    fi

    # Verify pip
    if ! command -v pip3 &>/dev/null; then
        warning "pip not found. Installing..."
        case "$os" in
            Termux) python -m ensurepip ;;
            *)      sudo python3 -m ensurepip ;;
        esac
        success "pip installed successfully!"
    else
        info "pip is already installed"
    fi

    # Install Python requirements
    if [ -f "requirements.txt" ]; then
        info "Installing Python dependencies from requirements.txt..."
        pip3 install -r requirements.txt
        success "Dependencies installed!"
    else
        warning "No requirements.txt found - skipping dependency installation"
    fi
}

# Create global symlink
create_symlink() {
    local os="$1"
    local install_path
    
    case "$os" in
        Termux) 
            install_path="/data/data/com.termux/files/usr/bin"
            use_sudo=0
            ;;
        Linux|MacOS) 
            install_path="/usr/local/bin"
            use_sudo=1
            ;;
        *) 
            warning "Unsupported OS for symlink"
            return 
            ;;
    esac

    local launcher_path="$PWD/.launcher"
    
    # Create launcher if it doesn't exist
    if [ ! -f "$launcher_path" ]; then
        create_launcher
    fi

    # Check if symlink already exists
    if [ -L "$install_path/phish" ]; then
        info "Updating existing symlink..."
        if [ "$use_sudo" -eq 1 ]; then
            sudo rm "$install_path/phish"
            sudo ln -sf "$launcher_path" "$install_path/phish"
        else
            rm "$install_path/phish"
            ln -sf "$launcher_path" "$install_path/phish"
        fi
    else
        info "Creating new symlink..."
        if [ "$use_sudo" -eq 1 ]; then
            sudo ln -sf "$launcher_path" "$install_path/phish"
        else
            ln -sf "$launcher_path" "$install_path/phish"
        fi
    fi
    
    # Verify symlink creation
    if [ -L "$install_path/phish" ]; then
        success "Symlink created: ${GREEN}phish${NC} → ${CYAN}$launcher_path${NC}"
        info "You can now run the tool with: ${GREEN}phish${NC}"
    else
        error "Symlink creation failed. Try manual command:"
        echo "ln -s $launcher_path $install_path/phish"
    fi
}

# Main setup routine
main() {
    show_banner
    
    # Check if in project root
    if [ ! -f "main.py" ]; then
        error "Run this script from Scarface project root!"
        exit 1
    fi

    local os=$(detect_os)
    info "Detected OS: ${CYAN}$os${NC}"
    
    create_launcher
    install_dependencies "$os"
    create_symlink "$os"
    
    echo -e "\n${GREEN}Setup completed successfully!${NC}"
    info "Start the tool with: ${GREEN}phish${NC}"
}

main
