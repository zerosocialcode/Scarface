#!/usr/bin/env bash

# ==============================================================================
# SCARFACE CROSS-PLATFORM INSTALLER
# Works on: Windows, Linux, macOS, Termux, WSL, Git Bash, Cygwin, MSYS2
# ==============================================================================

# Color definitions (compatible with all terminals)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${CYAN}[*] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[✔] $1${NC}"
}

print_error() {
    echo -e "${RED}[!] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

# Clear screen (platform-agnostic)
clear_screen() {
    printf "\033c" 2>/dev/null || clear 2>/dev/null || :
}

# Get script directory (works even with symlinks)
get_script_dir() {
    SOURCE="${BASH_SOURCE[0]}"
    while [ -h "$SOURCE" ]; do
        DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
        SOURCE="$(readlink "$SOURCE")"
        [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
    done
    echo "$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
}

# ==============================================================================
# DETECT PLATFORM AND ENVIRONMENT
# ==============================================================================

clear_screen

# Display banner
SCRIPT_DIR="$(get_script_dir)"
BANNER_FILE="$SCRIPT_DIR/assets/banners/setup.txt"
if [ -f "$BANNER_FILE" ]; then
    echo -e "${MAGENTA}"
    cat "$BANNER_FILE"
    echo -e "${NC}"
fi

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║          SCARFACE FRAMEWORK - UNIVERSAL INSTALLER           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

# Detect OS and environment
detect_environment() {
    local OS
    OS="$(uname -s)"
    
    case "${OS}" in
        Linux*)
            # Check for Termux (Android)
            if [ -d "/data/data/com.termux/files/usr" ]; then
                ENV_TYPE="termux"
                INSTALL_DIR="/data/data/com.termux/files/usr/bin"
                PYTHON_CMD="python"
                SUDO_CMD=""
                echo -e "${GREEN}[+] Termux (Android) environment detected${NC}"
            
            # Check for WSL (Windows Subsystem for Linux)
            elif grep -q -i microsoft /proc/version 2>/dev/null; then
                ENV_TYPE="wsl"
                INSTALL_DIR="/usr/local/bin"
                PYTHON_CMD="python3"
                SUDO_CMD="sudo"
                echo -e "${GREEN}[+] WSL (Windows Subsystem for Linux) detected${NC}"
            
            # Regular Linux
            else
                ENV_TYPE="linux"
                INSTALL_DIR="/usr/local/bin"
                PYTHON_CMD="python3"
                SUDO_CMD="sudo"
                echo -e "${GREEN}[+] Linux environment detected${NC}"
            fi
            ;;
        
        Darwin*)
            ENV_TYPE="macos"
            INSTALL_DIR="/usr/local/bin"
            PYTHON_CMD="python3"
            SUDO_CMD="sudo"
            echo -e "${GREEN}[+] macOS environment detected${NC}"
            ;;
        
        CYGWIN*|MINGW32*|MSYS*|MINGW*)
            ENV_TYPE="windows"
            
            # Detect specific Windows shell
            if [[ "$MSYSTEM" == "MINGW64" ]]; then
                echo -e "${GREEN}[+] Git Bash (MINGW64) detected${NC}"
            elif [[ "$MSYSTEM" == "MSYS" ]]; then
                echo -e "${GREEN}[+] MSYS2 detected${NC}"
            elif [[ "$OSTYPE" == "cygwin" ]]; then
                echo -e "${GREEN}[+] Cygwin detected${NC}"
            else
                echo -e "${GREEN}[+] Windows environment detected${NC}"
            fi
            
            # Windows-specific paths
            if [ -n "$USERPROFILE" ]; then
                WIN_HOME="$(cygpath -u "$USERPROFILE" 2>/dev/null || echo "$HOME")"
            else
                WIN_HOME="$HOME"
            fi
            
            INSTALL_DIR="$WIN_HOME/.local/bin"
            PYTHON_CMD="python"
            SUDO_CMD=""
            
            # Ensure install directory exists
            mkdir -p "$INSTALL_DIR"
            ;;
        
        *)
            ENV_TYPE="unknown"
            INSTALL_DIR="/usr/local/bin"
            PYTHON_CMD="python3"
            SUDO_CMD="sudo"
            echo -e "${YELLOW}[!] Unknown environment: ${OS}${NC}"
            echo -e "${CYAN}[*] Using fallback settings${NC}"
            ;;
    esac
    
    # Fallback for Python command if primary not found
    if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
        if command -v python3 >/dev/null 2>&1; then
            PYTHON_CMD="python3"
        elif command -v python >/dev/null 2>&1; then
            PYTHON_CMD="python"
        else
            print_error "Python not found! Please install Python first."
            exit 1
        fi
    fi
    
    # Detect Python version
    PYTHON_VERSION="$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)"
    echo -e "${CYAN}[*] Using Python ${PYTHON_VERSION} (${PYTHON_CMD})${NC}"
}

detect_environment

# ==============================================================================
# CHECK PREREQUISITES
# ==============================================================================

print_status "Checking prerequisites..."

# Check if running as root/sudo
if [ "$EUID" -eq 0 ] && [ "$ENV_TYPE" != "termux" ]; then
    print_warning "Running as root! It's safer to install as regular user."
    read -p "Continue as root? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for write permissions to install directory
if [ ! -w "$INSTALL_DIR" ] && [ "$ENV_TYPE" != "windows" ] && [ "$ENV_TYPE" != "termux" ]; then
    print_status "Install directory requires elevated permissions"
    
    if command -v sudo >/dev/null 2>&1; then
        SUDO_CMD="sudo"
        print_status "Will use sudo for installation"
    elif command -v doas >/dev/null 2>&1; then
        SUDO_CMD="doas"
        print_status "Will use doas for installation"
    else
        print_error "No privilege elevation tool found (sudo/doas)"
        print_error "Please run this script as root or install manually"
        exit 1
    fi
fi

# ==============================================================================
# INSTALL DEPENDENCIES
# ==============================================================================

print_status "Installing Python dependencies..."

REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    # Try different pip installation methods
    if command -v pip3 >/dev/null 2>&1; then
        PIP_CMD="pip3"
    elif command -v pip >/dev/null 2>&1; then
        PIP_CMD="pip"
    else
        # Try to install pip if not found
        print_status "pip not found, attempting to install..."
        if [ "$ENV_TYPE" = "termux" ]; then
            pkg install python-pip -y
        elif command -v apt-get >/dev/null 2>&1; then
            $SUDO_CMD apt-get install python3-pip -y
        elif command -v yum >/dev/null 2>&1; then
            $SUDO_CMD yum install python3-pip -y
        elif command -v brew >/dev/null 2>&1; then
            brew install python3
        fi
        
        # Check again
        if command -v pip3 >/dev/null 2>&1; then
            PIP_CMD="pip3"
        else
            PIP_CMD="pip"
        fi
    fi
    
    # Install with appropriate flags for environment
    print_status "Installing with $PIP_CMD..."
    
    case "$ENV_TYPE" in
        "termux")
            $PIP_CMD install -r "$REQUIREMENTS_FILE" --user
            ;;
        "windows")
            $PIP_CMD install -r "$REQUIREMENTS_FILE" --user
            ;;
        *)
            # Try --break-system-packages first (modern pip)
            $PIP_CMD install -r "$REQUIREMENTS_FILE" --break-system-packages 2>/dev/null || \
            # Fallback to --user
            $PIP_CMD install -r "$REQUIREMENTS_FILE" --user 2>/dev/null || \
            # Last resort: global install
            $PIP_CMD install -r "$REQUIREMENTS_FILE"
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
    else
        print_error "Some dependencies failed to install"
        print_warning "Trying with verbose output..."
        $PIP_CMD install -r "$REQUIREMENTS_FILE"
        if [ $? -ne 0 ]; then
            print_warning "Continuing with installation despite dependency issues..."
        fi
    fi
else
    print_error "requirements.txt not found at: $REQUIREMENTS_FILE"
    print_warning "Skipping dependency installation"
fi

# ==============================================================================
# CREATE GLOBAL COMMAND
# ==============================================================================

print_status "Creating global 'scarface' command..."

# Find the main console script
CONSOLE_SCRIPTS=(
    "$SCRIPT_DIR/src/console.py"
    "$SCRIPT_DIR/console.py"
    "$SCRIPT_DIR/scarface.py"
    "$SCRIPT_DIR/main.py"
)

CONSOLE_SCRIPT=""
for script in "${CONSOLE_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        CONSOLE_SCRIPT="$script"
        break
    fi
done

if [ -z "$CONSOLE_SCRIPT" ]; then
    print_error "Could not find main Python script!"
    print_error "Checked: ${CONSOLE_SCRIPTS[*]}"
    exit 1
fi

print_success "Found main script: $CONSOLE_SCRIPT"

# Convert paths for Windows if needed
if [ "$ENV_TYPE" = "windows" ]; then
    # Convert to Windows path for Python
    if command -v cygpath >/dev/null 2>&1; then
        CONSOLE_SCRIPT_WIN="$(cygpath -w "$CONSOLE_SCRIPT")"
        SCRIPT_DIR_WIN="$(cygpath -w "$SCRIPT_DIR")"
    else
        # Fallback for Git Bash without cygpath
        CONSOLE_SCRIPT_WIN="${CONSOLE_SCRIPT//\//\\}"
        SCRIPT_DIR_WIN="${SCRIPT_DIR//\//\\}"
    fi
fi

# Create appropriate wrapper based on environment
create_wrapper() {
    local wrapper_path="$1"
    
    case "$ENV_TYPE" in
        "windows")
            # Create .bat wrapper for Windows CMD
            cat > "${wrapper_path}.bat" << EOF
@echo off
cd /d "$SCRIPT_DIR_WIN"
$PYTHON_CMD "$CONSOLE_SCRIPT_WIN" %*
EOF
            
            # Create .sh wrapper for Git Bash/Cygwin
            cat > "$wrapper_path" << EOF
#!/usr/bin/env bash
cd "$SCRIPT_DIR"
$PYTHON_CMD "$CONSOLE_SCRIPT" "\$@"
EOF
            chmod +x "$wrapper_path"
            ;;
        
        *)
            # Unix-like systems (Linux, macOS, Termux, WSL)
            cat > "$wrapper_path" << EOF
#!/usr/bin/env bash
cd "$SCRIPT_DIR"
$PYTHON_CMD "$CONSOLE_SCRIPT" "\$@"
EOF
            chmod +x "$wrapper_path"
            ;;
    esac
}

# Create temporary wrapper
TEMP_WRAPPER="$SCRIPT_DIR/scarface_wrapper_tmp"
create_wrapper "$TEMP_WRAPPER"

# Install the wrapper
install_wrapper() {
    local target_name="scarface"
    
    # Remove old wrapper if exists
    rm -f "$INSTALL_DIR/$target_name" "$INSTALL_DIR/$target_name.bat" 2>/dev/null
    
    case "$ENV_TYPE" in
        "windows")
            # Install both .sh and .bat versions
            cp "$TEMP_WRAPPER" "$INSTALL_DIR/$target_name"
            if [ -f "${TEMP_WRAPPER}.bat" ]; then
                cp "${TEMP_WRAPPER}.bat" "$INSTALL_DIR/$target_name.bat"
            fi
            ;;
        *)
            # Unix-like: use sudo if needed
            if [ -w "$INSTALL_DIR" ]; then
                cp "$TEMP_WRAPPER" "$INSTALL_DIR/$target_name"
            else
                $SUDO_CMD cp "$TEMP_WRAPPER" "$INSTALL_DIR/$target_name"
            fi
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        print_success "Wrapper installed to: $INSTALL_DIR/$target_name"
        
        # Clean up temp file
        rm -f "$TEMP_WRAPPER" "${TEMP_WRAPPER}.bat" 2>/dev/null
        
        return 0
    else
        print_error "Failed to install wrapper"
        return 1
    fi
}

# Attempt installation
if install_wrapper; then
    # ==========================================================================
    # UPDATE PATH AND VERIFY INSTALLATION
    # ==========================================================================
    
    print_status "Verifying installation..."
    
    # Add to PATH if not already present (for user installations)
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        print_status "Adding install directory to PATH..."
        
        case "$ENV_TYPE" in
            "windows")
                # Windows: add to .bashrc and .bash_profile
                for rc_file in "$WIN_HOME/.bashrc" "$WIN_HOME/.bash_profile"; do
                    if [ -f "$rc_file" ]; then
                        if ! grep -q "export PATH.*$INSTALL_DIR" "$rc_file"; then
                            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$rc_file"
                        fi
                    fi
                done
                
                # Also update system PATH (requires admin, so just warn)
                print_warning "For Command Prompt/PowerShell, add $INSTALL_DIR to your system PATH manually"
                ;;
            
            "termux")
                # Termux already has user bin in PATH
                ;;
            
            *)
                # Unix: add to .bashrc, .zshrc, .profile
                for rc_file in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
                    if [ -f "$rc_file" ]; then
                        if ! grep -q "export PATH.*$INSTALL_DIR" "$rc_file"; then
                            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$rc_file"
                        fi
                    fi
                done
                ;;
        esac
        
        print_warning "You may need to restart your terminal or run:"
        case "$SHELL" in
            *zsh*) echo -e "${CYAN}  source ~/.zshrc${NC}" ;;
            *fish*) echo -e "${CYAN}  source ~/.config/fish/config.fish${NC}" ;;
            *) echo -e "${CYAN}  source ~/.bashrc${NC}" ;;
        esac
    fi
    
    # Test the command
    print_status "Testing 'scarface' command..."
    
    # Give a moment for PATH updates
    if command -v scarface >/dev/null 2>&1; then
        print_success "'scarface' command is ready!"
        echo
        echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║                 INSTALLATION COMPLETE!                       ║${NC}"
        echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
        echo
        echo -e "You can now run: ${CYAN}scarface${NC}"
        echo
        echo -e "${BLUE}Examples:${NC}"
        echo -e "  scarface --help"
        echo -e "  scarface start"
        echo -e "  scarface --version"
        
        # Quick test
        echo
        print_status "Quick test:"
        if scarface --help >/dev/null 2>&1; then
            print_success "Command works correctly!"
        else
            print_warning "Command installed but test failed"
            print_warning "Try running: $INSTALL_DIR/scarface"
        fi
        
    else
        print_warning "'scarface' command not found in PATH"
        echo -e "${CYAN}You can run it directly with:${NC}"
        echo -e "  $INSTALL_DIR/scarface"
        echo
        echo -e "${YELLOW}Or add the directory to your PATH manually:${NC}"
        echo -e "  export PATH=\"$INSTALL_DIR:\$PATH\""
    fi
    
else
    # Alternative installation method
    print_error "Could not install to $INSTALL_DIR"
    echo
    echo -e "${YELLOW}Alternative installation methods:${NC}"
    echo
    echo -e "1. ${CYAN}Run from current directory:${NC}"
    echo -e "   cd \"$SCRIPT_DIR\""
    echo -e "   $PYTHON_CMD \"$CONSOLE_SCRIPT\""
    echo
    echo -e "2. ${CYAN}Create alias in your shell:${NC}"
    echo -e "   Add this to your shell config file (.bashrc, .zshrc, etc):"
    echo -e "   alias scarface='cd \"$SCRIPT_DIR\" && $PYTHON_CMD \"$CONSOLE_SCRIPT\"'"
    echo
    echo -e "3. ${CYAN}Manual installation:${NC}"
    echo -e "   Copy the wrapper manually:"
    echo -e "   cp \"$TEMP_WRAPPER\" ~/bin/scarface"
    echo -e "   chmod +x ~/bin/scarface"
fi

# Cleanup
rm -f "$TEMP_WRAPPER" "${TEMP_WRAPPER}.bat" 2>/dev/null

echo
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Thank you for installing Scarface Framework!${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
