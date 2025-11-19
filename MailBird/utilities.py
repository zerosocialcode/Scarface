import os
import sys
import shutil
from pathlib import Path

class ColorUtils:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class DisplayUtils:
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_banner(self, banner_path, color=ColorUtils.GREEN):
        try:
            banner_file = Path(banner_path)
            if banner_file.exists():
                with open(banner_file, 'r', encoding='utf-8') as f:
                    banner_content = f.read()
                print(f"{color}{banner_content}{ColorUtils.RESET}")
        except Exception:
            print("Banner not available")

    def print_progress_bar(self, iteration, total, prefix='Processing', suffix='', decimals=0, fill='=', printEnd="\r"):
        try:
            columns = shutil.get_terminal_size().columns
        except Exception:
            columns = 80

        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        percent_str = f"{percent}%"
        
        prefix_fmt = f"{ColorUtils.BLUE}[*]{ColorUtils.RESET} {prefix}"
        
        static_len = len(prefix) + len(suffix) + len(percent_str) + 10
        bar_length = max(1, columns - static_len)
        
        filled_length = int(bar_length * iteration // total)
        
        if iteration == total:
            bar = fill * filled_length + ' ' * (bar_length - filled_length)
        else:
            if filled_length == 0:
                bar = '>' + ' ' * (bar_length - 1)
            else:
                bar = fill * (filled_length - 1) + '>' + ' ' * (bar_length - filled_length)
        
        output = f'\r{prefix_fmt} [{bar}] {percent_str} {suffix}'
        
        sys.stdout.write(output)
        sys.stdout.flush()
        
        if iteration == total:
            print()

    def dynamic_print(self, text, color=ColorUtils.RESET, end='\r'):
        try:
            columns = shutil.get_terminal_size().columns
        except:
            columns = 80
            
        sys.stdout.write('\r' + ' ' * (columns - 1) + '\r')
        
        if color == ColorUtils.GREEN:
            symbol = f"{ColorUtils.GREEN}[+]{ColorUtils.RESET}"
        elif color == ColorUtils.RED:
            symbol = f"{ColorUtils.RED}[-]{ColorUtils.RESET}"
        elif color == ColorUtils.YELLOW:
            symbol = f"{ColorUtils.BLUE}[*]{ColorUtils.RESET}"
        else:
            symbol = f"{ColorUtils.BLUE}[*]{ColorUtils.RESET}"

        sys.stdout.write(f"{symbol} {text}")
        sys.stdout.flush()
        if end == '\n':
            sys.stdout.write('\n')
