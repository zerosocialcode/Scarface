import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import subprocess
from termcolor import colored

# ========== COLOR FUNCTIONS ==========
def prompt(text):
    return input(colored(text, "cyan", attrs=["bold"]))

def print_success(msg):
    print(colored(msg, "green"))

def print_error(msg):
    print(colored(msg, "red"))

def print_info(msg):
    print(colored(msg, "white"))

# ========== CLONER CLASS ==========
class Cloner:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.ssl_verify = True
        # Corrected: Save cloned sites to Scarface/sites/
        self.base_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), 
                '..', 
                'sites'
            )
        )

    def clone_site(self, url, folder_name):
        try:
            output_dir = os.path.join(self.base_dir, folder_name)
            os.makedirs(output_dir, exist_ok=True)
            print_info(f"[*] Cloning: {url}")

            if self._try_wget_clone(url, output_dir):
                self._inject_viewport_meta(output_dir)
                print_success(f"[+] Successfully cloned to: {output_dir}")
                return True

            if self._python_clone_with_resources(url, output_dir):
                self._inject_viewport_meta(output_dir)
                return True
            return False

        except Exception as e:
            print_error(f"[!] Error: {str(e)}")
            return False

    def _try_wget_clone(self, url, output_dir):
        try:
            cmd = [
                'wget',
                '--convert-links',
                '--adjust-extension',
                '--page-requisites',
                '--no-check-certificate' if not self.ssl_verify else '',
                '--no-host-directories',
                '--cut-dirs=1',
                '-U', self.user_agent,
                '-P', output_dir,
                url
            ]
            cmd = [arg for arg in cmd if arg]
            subprocess.run(cmd, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print_error(f"[!] Error running wget: {str(e)}")
            return False

    def _python_clone_with_resources(self, url, output_dir):
        try:
            req = requests.get(url, headers={'User-Agent': self.user_agent}, verify=self.ssl_verify)
            req.raise_for_status()
            soup = BeautifulSoup(req.text, 'html.parser')

            main_file = os.path.join(output_dir, "index.html")
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print_success(f"[+] Main HTML saved as: {main_file}")

            for tag, attr in [("link", "href"), ("script", "src"), ("img", "src")]:
                for resource in soup.find_all(tag):
                    resource_url = resource.get(attr)
                    if resource_url:
                        full_url = urljoin(url, resource_url)
                        self._download_resource(full_url, output_dir)

            return True
        except requests.RequestException as e:
            print_error(f"[!] Connection Error: {e}")
            return False

    def _download_resource(self, resource_url, output_dir):
        try:
            response = requests.get(resource_url, 
                                   headers={'User-Agent': self.user_agent},
                                   verify=self.ssl_verify,
                                   stream=True)
            response.raise_for_status()

            parsed_url = urlparse(resource_url)
            filename = os.path.basename(parsed_url.path) or "resource"
            filepath = os.path.join(output_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print_info(f"[+] Downloaded: {filename}")
        except requests.RequestException as e:
            print_error(f"[!] Failed to download: {resource_url} ({e})")

    def _inject_viewport_meta(self, output_dir):
        """Injects responsive viewport meta tag into all HTML files"""
        for root, _, files in os.walk(output_dir):
            for file in files:
                if file.lower().endswith(('.html', '.htm')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r+', encoding='utf-8') as f:
                            content = f.read()
                            soup = BeautifulSoup(content, 'html.parser')
                            
                            # Check for existing viewport tag
                            viewport = soup.find('meta', attrs={'name': 'viewport'})
                            
                            if not viewport:
                                # Create new viewport tag if none exists
                                viewport = soup.new_tag('meta')
                                viewport.attrs['name'] = 'viewport'
                                viewport.attrs['content'] = 'width=device-width, initial-scale=1.0'
                                
                                # Insert into head or create head if missing
                                head = soup.head
                                if not head:
                                    head = soup.new_tag('head')
                                    if soup.html:
                                        soup.html.insert(0, head)
                                    else:
                                        soup.insert(0, head)
                                
                                head.insert(0, viewport)
                                
                                # Save changes
                                f.seek(0)
                                f.write(str(soup))
                                f.truncate()
                                print_success(f"[+] Added viewport meta to: {file_path}")
                            else:
                                print_info(f"[*] Viewport meta already exists in: {file_path}")
                    except Exception as e:
                        print_error(f"[!] Failed to inject viewport in {file_path}: {str(e)}")

def main():
    try:
        # Removed: Banner, title, developer info, and "Running Scarface Cloner" output
        url = prompt("\nEnter target URL: ").strip()
        if not url:
            print_error("\n[!] URL cannot be empty")
            sys.exit(1)
            
        folder_name = prompt("Enter folder name (will be created in Scarface/sites/): ").strip()
        if not folder_name:
            print_error("\n[!] Folder name cannot be empty")
            sys.exit(1)

        cloner = Cloner()
        if cloner.clone_site(url, folder_name):
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
