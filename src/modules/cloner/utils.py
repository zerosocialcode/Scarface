import sys
import os
import shutil
from termcolor import colored

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    banner_path = os.path.join(base_dir, '..', '..', '..', 'assets', 'banners', 'cloner.txt')
    
    try:
        with open(banner_path, 'r', encoding='utf-8') as f:
            banner_content = f.read()
        print(colored(banner_content, "cyan", attrs=["bold"]))
    except FileNotFoundError:
        pass
    except Exception:
        pass

def print_step(message):
    print(colored(f"\n  [*] {message}", "blue"))

def print_status(message):
    try:
        width = shutil.get_terminal_size().columns
    except OSError:
        width = 80
    
    status_text = f"  {message}"
    
    if len(status_text) > width:
        status_text = status_text[:width - 3] + "..."
        
    sys.stdout.write('\r' + ' ' * width + '\r')
    sys.stdout.write(colored(status_text, "blue"))
    sys.stdout.flush()

def clear_status():
    try:
        width = shutil.get_terminal_size().columns
    except OSError:
        width = 80
    sys.stdout.write('\r' + ' ' * width + '\r')
    sys.stdout.flush()

def prompt(text):
    return input(colored(f"\n  [?] {text}: ", "cyan", attrs=["bold"]))

def print_success(msg):
    print(colored(f"\n  [+] {msg}", "green", attrs=["bold"]))

def print_error(msg):
    print(colored(f"\n  [!] {msg}", "red", attrs=["bold"]))

def print_info(msg):
    print(colored(f"  [*] {msg}", "blue"))
