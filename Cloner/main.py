import sys
import os
from core import Cloner
from utils import prompt, print_error, print_success

def main():
    try:
        url = prompt("\nEnter target URL: ").strip()
        if not url:
            print_error("\n[!] URL cannot be empty")
            sys.exit(1)
            
        folder_name = prompt("Enter folder name (will be created in sites/): ").strip()
        if not folder_name:
            print_error("\n[!] Folder name cannot be empty")
            sys.exit(1)

        depth = prompt("Enter depth (0 for single page, 1 for linked pages, etc.): ").strip()
        try:
            depth = int(depth)
            if depth < 0:
                raise ValueError
        except ValueError:
            print_error("\n[!] Depth must be a positive integer")
            sys.exit(1)

        cloner = Cloner()
        if cloner.clone_site(url, folder_name, depth):
            final_path = os.path.join(cloner.base_dir, folder_name)
            print_success(f"\n[+] Clone successful! Saved to: {final_path}")
        else:
            print_error("\n[!] Cloning failed")
            
    except KeyboardInterrupt:
        print_error("\n\n[!] Operation cancelled by user")
        sys.exit(1)
        
    except Exception as e:
        print_error(f"\n[!] Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
