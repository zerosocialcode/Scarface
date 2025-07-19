import subprocess
import re
import sys
import time

def main():
    if len(sys.argv) < 2:
        print("Usage: python localtunnel.py [PORT]", file=sys.stderr)
        sys.exit(1)
    port = sys.argv[1]
    proc = subprocess.Popen(
        ["lt", "--port", port],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    url_regex = re.compile(r"https://[a-zA-Z0-9\-]+\.loca\.lt")
    got_url = False
    start_time = time.time()
    while True:
        line = proc.stdout.readline()
        if not line:
            if time.time() - start_time > 30:
                print("Error: Timeout waiting for LocalTunnel URL", file=sys.stderr)
                proc.terminate()
                sys.exit(1)
            continue
        match = url_regex.search(line)
        if match and not got_url:
            print(match.group(0), flush=True)
            got_url = True
        if got_url:
            continue

if __name__ == "__main__":
    main()
