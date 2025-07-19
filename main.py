import os
import sys
import subprocess
from termcolor import colored
import platform
import json

# Clear screen command based on OS
CLEAR = 'cls' if platform.system() == 'Windows' else 'clear'

def clear_screen():
    os.system(CLEAR)

def load_banner():
    """Loads banner from .banner.txt file only"""
    try:
        with open('banner/banner.txt', 'r') as f:
            banner = f.read()
        return colored(banner, 'green', attrs=['bold'])
    except FileNotFoundError:
        # No banner if file not found
        return ""

def load_config():
    """Loads configuration from .dev.json"""
    try:
        with open('developer/dev.json', 'r') as f:
            config = json.load(f)
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        # Default config if file not found or invalid
        return {
            "tool_name": "",
            "developer": ""
        }

def print_banner():
    """Prints the banner and header information (if any)"""
    config = load_config()
    banner = load_banner()
    if banner.strip():
        print(banner)
    if config.get("tool_name"):
        print(colored(f"\n{config['tool_name']}", 'red', attrs=['underline']))
    if config.get("developer"):
        print(colored(f"developer: {config['developer']}\n", 'red', attrs=['underline']))
    print("-" * os.get_terminal_size().columns)

def refresh_screen(tools=None, current_selection=None):
    """Clears and re-renders the screen with banner"""
    clear_screen()
    print_banner()
    if tools:
        list_tools(tools)
    if current_selection:
        print()

def scan_tools(base_path):
    tools = {}
    for entry in os.listdir(base_path):
        tool_path = os.path.join(base_path, entry)
        if os.path.isdir(tool_path):
            for main_file in ["__main__.py", "main.py"]:
                main_path = os.path.join(tool_path, main_file)
                if os.path.isfile(main_path):
                    tools[entry] = main_path
    return tools

def list_tools(tools):
    for idx, name in enumerate(tools.keys(), 1):
        print(colored(f"{idx}. {name}", 'cyan'))

def select_tool(tools, main_prompt):
    while True:
        try:
            refresh_screen(tools)
            choice = input(colored(f"\n{main_prompt}", 'yellow'))
            if not choice:
                continue
            choice = int(choice)
            if 1 <= choice <= len(tools):
                tool_name = list(tools.keys())[choice-1]
                return tool_name, tools[tool_name]
            print(colored("Invalid number. Try again.", 'red'))
        except ValueError:
            print(colored("Please enter a number.", 'red'))
        except KeyboardInterrupt:
            graceful_exit()

def run_tool(tool_main_path, tool_dir, tool_name):
    refresh_screen(current_selection=tool_name)
    cmd = [sys.executable, os.path.basename(tool_main_path)]
    try:
        subprocess.run(cmd, cwd=tool_dir, check=True)
    except KeyboardInterrupt:
        pass  # Let the tool handle its own interrupt
    except subprocess.CalledProcessError as e:
        print(colored(f"Tool error: {e}", 'red'))
    finally:
        input(colored("\nPress Enter to return to menu...", 'yellow'))

def graceful_exit():
    clear_screen()
    print(colored("\nGoodbye!", 'red', attrs=['bold']))
    sys.exit(0)

def main():
    # Detect main project/folder name
    main_folder_name = os.path.basename(os.path.abspath(os.path.dirname(__file__))).lower()
    main_prompt = f"{main_folder_name}> "
    try:
        base_path = os.getcwd()
        tools = scan_tools(base_path)
        if not tools:
            print(colored("No tools detected in this directory.", 'red'))
            sys.exit(1)

        while True:
            tool_name, tool_main_path = select_tool(tools, main_prompt)
            tool_dir = os.path.dirname(tool_main_path)
            run_tool(tool_main_path, tool_dir, tool_name)
            
    except KeyboardInterrupt:
        graceful_exit()

if __name__ == "__main__":
    main()
