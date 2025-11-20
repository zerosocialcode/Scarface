import sys
import os
from core import Cloner
from utils import (
    prompt, print_error, print_success, 
    clear_screen, print_banner, 
    print_status, clear_status
)

def main():
    clear_screen()
    print_banner()
    
    try:
        url = prompt("Enter target URL").strip()
        if not url:
            print_error("URL cannot be empty")
            sys.exit(1)
            
        folder_name = prompt("Enter local save name (e.g., 'my-site')").strip()
        if not folder_name:
            print_error("Folder name cannot be empty")
            sys.exit(1)

        depth = prompt("Enter clone depth (0=single page, 1=links, etc.)").strip()
        try:
            depth = int(depth)
            if depth < 0:
                raise ValueError
        except ValueError:
            print_error("Depth must be a non-negative number")
            sys.exit(1)

        cloner = Cloner()
        
        cloner.print_info = print_status
        cloner.print_success = print_status
        cloner.print_error = print_error
        
        clone_success = cloner.clone_site(url, folder_name, depth)
        
        clear_status()

        if clone_success:
            print_success("Clone Complete!")
        else:
            print_error("Cloning failed. Check logs above.")
            
    except KeyboardInterrupt:
        clear_status()
        print_error("\nOperation cancelled by user")
        sys.exit(1)
        
    except Exception as e:
        clear_status()
        print_error(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
