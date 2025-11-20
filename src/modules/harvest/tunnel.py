import os
import sys
import subprocess
import re
import time

def run_expose_and_get_url(option, expose_dir, port):
    expose_scripts = {
        1: "cloudflared.py",
        2: "ngrok.py",
        3: "localtunnel.py"
    }
    url_patterns = {
        1: r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com",
        2: r"https://[a-zA-Z0-9\-]+\.ngrok-free\.app",
        3: r"https://[a-zA-Z0-9\-]+\.loca\.lt"
    }
    if option in expose_scripts:
        script = os.path.join(expose_dir, expose_scripts[option])
        proc = subprocess.Popen(
            [sys.executable, script, str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        url_regex = re.compile(url_patterns[option])
        url = None
        start = time.time()
        max_wait = 30
        while time.time() - start < max_wait and url is None:
            line = proc.stdout.readline()
            if not line:
                continue
            match = url_regex.search(line)
            if match:
                url = match.group(0)
                break
        if url:
            return url, proc
        else:
            if proc.poll() is None:
                proc.terminate()
            return None, None
    elif option == 4:
        return f"http://localhost:{port}", None
    elif option == 5:
        return None, None
