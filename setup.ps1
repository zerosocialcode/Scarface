# setup.ps1
# Set Encoding for special characters
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Color definitions
$RED = "`e[0;31m"
$GREEN = "`e[0;32m"
$CYAN = "`e[0;36m"
$YELLOW = "`e[0;33m"
$NC = "`e[0m"

# Configuration
$INSTALL_DIR = Join-Path $HOME "bin"
$PROJECT_DIR = Get-Location
$CONSOLE_SCRIPT = Join-Path $PROJECT_DIR "src\console.py"

Clear-Host

# --- DISPLAY BANNER ---
$BANNER_FILE = "assets/banners/setup.txt"
if (Test-Path $BANNER_FILE) {
    Write-Host "${CYAN}" -NoNewline
    Get-Content $BANNER_FILE
    Write-Host "${NC}" -NoNewline
}

Write-Host "${CYAN}   Scarface Framework Installer (PowerShell)${NC}"
Write-Host "----------------------------------------"

# 1. Detect and Prepare Environment
Write-Host "${GREEN}[+] Windows (PowerShell) environment detected.${NC}"

if (!(Test-Path $INSTALL_DIR)) {
    New-Item -ItemType Directory -Force -Path $INSTALL_DIR | Out-Null
    Write-Host "${CYAN}[*] Created installation directory: $INSTALL_DIR${NC}"
}

# 2. Install Dependencies
Write-Host "${CYAN}[*] Installing Python dependencies...${NC}"
if (Test-Path "requirements.txt") {
    $PIP_CMD = if (Get-Command pip3 -ErrorAction SilentlyContinue) { "pip3" } else { "pip" }
    
    if (!(Get-Command $PIP_CMD -ErrorAction SilentlyContinue)) {
        Write-Host "${RED}[!] Python pip not found! Please install Python 3 first.${NC}"
        exit
    }

    # Attempt installation
    & $PIP_CMD install -r requirements.txt --user --break-system-packages 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "${GREEN}[✔] Dependencies installed successfully.${NC}"
    } else {
        Write-Host "${YELLOW}[!] Trying installation with verbose output...${NC}"
        & $PIP_CMD install -r requirements.txt
    }
} else {
    Write-Host "${RED}[!] requirements.txt not found!${NC}"
    exit
}

# 3. Create Executable Wrapper
Write-Host "${CYAN}[*] Configuring 'scarface' command...${NC}"

if (!(Test-Path $CONSOLE_SCRIPT)) {
    Write-Host "${YELLOW}[*] Looking for console.py in other locations...${NC}"
    $FOUND = Get-ChildItem -Path . -Filter "console.py" -Recurse | Select-Object -First 1
    if ($FOUND) {
        $CONSOLE_SCRIPT = $FOUND.FullName
        Write-Host "${GREEN}[*] Found console.py at: $CONSOLE_SCRIPT${NC}"
    } else {
        Write-Host "${RED}[!] Could not find console.py${NC}"
        exit
    }
}

# Create a .ps1 wrapper script
$WRAPPER_PS1 = @"
# Scarface PowerShell Wrapper
Set-Location "$PROJECT_DIR"
python "$CONSOLE_SCRIPT" `$args
"@

$WRAPPER_PATH = Join-Path $INSTALL_DIR "scarface.ps1"
Set-Content -Path $WRAPPER_PATH -Value $WRAPPER_PS1

# 4. Update PATH for current session and permanently
$CURRENT_PATH = [Environment]::GetEnvironmentVariable("Path", "User")
if ($CURRENT_PATH -notlike "*$INSTALL_DIR*") {
    $NEW_PATH = "$CURRENT_PATH;$INSTALL_DIR"
    [Environment]::SetEnvironmentVariable("Path", $NEW_PATH, "User")
    $env:Path += ";$INSTALL_DIR"
    Write-Host "${CYAN}[*] Added $INSTALL_DIR to User PATH variable.${NC}"
}

# 5. Finalize
if (Test-Path $WRAPPER_PATH) {
    Write-Host "${GREEN}[✔] Successfully installed!${NC}"
    Write-Host "`nYou can now run the tool by typing: ${GREEN}scarface${NC}"
    Write-Host "${YELLOW}Note: You may need to restart your terminal for PATH changes to take full effect.${NC}"
    
    Write-Host "`n${CYAN}[*] Testing installation...${NC}"
    if (Get-Command scarface -ErrorAction SilentlyContinue) {
        Write-Host "${GREEN}[✔] 'scarface' command is available in your PATH${NC}"
    } else {
        Write-Host "${YELLOW}[!] Command not yet in PATH. Use: & '$WRAPPER_PATH'${NC}"
    }
} else {
    Write-Host "${RED}[!] Failed to create wrapper script.${NC}"
}