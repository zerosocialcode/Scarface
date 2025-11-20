import subprocess
import re
import sys
import time

def main():
    if len(sys.argv) < 2:
        print("Usage: python cloudflared.py [PORT]", file=sys.stderr)
        sys.exit(1)
    port = sys.argv[1]
    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    url_regex = re.compile(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com")
    start_time = time.time()
    got_url = False
    while True:
        line = proc.stdout.readline()
        if not line:
            if time.time() - start_time > 30:
                print("Error: Timeout waiting for Cloudflare URL", file=sys.stderr)
                proc.terminate()
                sys.exit(1)
            continue
        match = url_regex.search(line)
        if match and not got_url:
            print(match.group(0), flush=True)
            got_url = True
        if got_url:
            # Keep printing output in case of errors, but don't exit!
            continue

if __name__ == "__main__":
    main()
