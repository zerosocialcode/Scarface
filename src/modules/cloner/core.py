import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import subprocess
from utils import print_info, print_success, print_error

class Cloner:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.ssl_verify = True
        self.base_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), 
                '..', '..', '..', 
                'data', 'sites'
            )
        )
        self.visited_urls = set()
        self.domain = None
        
        self.print_info = print_info
        self.print_success = print_success
        self.print_error = print_error

    def clone_site(self, url, folder_name, depth=1):
        try:
            output_dir = os.path.join(self.base_dir, folder_name)
            os.makedirs(output_dir, exist_ok=True)
            
            self.print_info(f"Cloning: {url} with depth {depth}")
            
            parsed = urlparse(url)
            self.domain = f"{parsed.scheme}://{parsed.netloc}"
            
            success = False
            if self._try_wget_clone(url, output_dir, depth):
                success = True
            elif self._python_clone_with_resources(url, output_dir, depth):
                 success = True

            if success:
                self.print_info("Injecting viewport meta tags...")
                self._inject_viewport_meta(output_dir)
                self.print_success("Clone finalized.")
                return True
                
            return False

        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            return False

    def _try_wget_clone(self, url, output_dir, depth):
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
                '--level', str(depth),
                '--recursive',
                '--domains', urlparse(url).netloc,
                url
            ]
            cmd = [arg for arg in cmd if arg]
            
            self.print_info("Running wget mirror...")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.print_info("wget mirror complete.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.print_error(f"Error running wget: {str(e)}")
            if hasattr(e, 'stderr'):
                self.print_error(f"wget stderr: {e.stderr}")
            return False

    def _python_clone_with_resources(self, url, output_dir, depth):
        if depth < 0 or url in self.visited_urls:
            return True
            
        self.visited_urls.add(url)
        
        try:
            self.print_info(f"Fetching: {url}")
            req = requests.get(url, headers={'User-Agent': self.user_agent}, verify=self.ssl_verify)
            req.raise_for_status()
            soup = BeautifulSoup(req.text, 'html.parser')

            relative_path = urlparse(url).path.lstrip('/')
            if not relative_path:
                relative_path = 'index.html'
            elif not relative_path.endswith('.html'):
                relative_path = os.path.join(relative_path, 'index.html')
                
            file_path = os.path.join(output_dir, relative_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            
            self.print_info(f"Saved: {relative_path}")

            for tag, attr in [("link", "href"), ("script", "src"), ("img", "src")]:
                for resource in soup.find_all(tag):
                    resource_url = resource.get(attr)
                    if resource_url:
                        full_url = urljoin(url, resource_url)
                        self._download_resource(full_url, output_dir)

            if depth > 0:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    
                    if (full_url.startswith(self.domain) and 
                        full_url not in self.visited_urls and
                        not any(full_url.endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.zip'])):
                        self._python_clone_with_resources(full_url, output_dir, depth-1)

            return True
        except requests.RequestException as e:
            self.print_error(f"Connection Error: {e}")
            return False

    def _download_resource(self, resource_url, output_dir):
        try:
            self.print_info(f"Downloading: {os.path.basename(resource_url)}")
            response = requests.get(resource_url, 
                                 headers={'User-Agent': self.user_agent},
                                 verify=self.ssl_verify,
                                 stream=True)
            response.raise_for_status()

            parsed_url = urlparse(resource_url)
            relative_path = parsed_url.path.lstrip('/')
            if not relative_path:
                relative_path = os.path.basename(parsed_url.path) if parsed_url.path else 'resource.dat'
                
            filepath = os.path.join(output_dir, relative_path)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            self.print_info(f"Downloaded: {relative_path}")
        except requests.RequestException as e:
            self.print_error(f"Failed to download: {resource_url} ({e})")

    def _inject_viewport_meta(self, output_dir):
        from meta import inject_viewport
        inject_viewport(output_dir, self.print_success, self.print_error)
