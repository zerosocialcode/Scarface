import os
import sys
import subprocess
import time
import atexit
import signal
import socket
import tempfile
import shutil

def launch_php_server(site_root, main_file, port=None):
    """PHP server with guaranteed cleanup"""
    php_exec = shutil.which('php')
    if not php_exec:
        raise RuntimeError("PHP not found in PATH")

    rel_main = os.path.relpath(main_file, site_root)
    
    proc = subprocess.Popen(
        [php_exec, "-S", f"0.0.0.0:{port or 0}", "-t", site_root],
        cwd=site_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE
    )

    actual_port = port
    if not port:
        for _ in range(10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', 0))
                    actual_port = s.getsockname()[1]
                    break
            except:
                time.sleep(0.3)
        else:
            proc.terminate()
            raise RuntimeError("Could not determine server port")

    def cleanup():
        try:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
        except:
            pass

    atexit.register(cleanup)
    
    def handle_sigint(signum, frame):
        cleanup()
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_sigint)

    return proc, actual_port
