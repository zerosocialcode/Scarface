import subprocess
import re
import time

def main():
    proc = subprocess.Popen(
        ["ngrok", "http", "8080", "--log=stdout"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    url_regex = re.compile(r"https://[a-zA-Z0-9\-]+\.ngrok-free\.app")
    
    while True:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        match = url_regex.search(line)
        if match:
            print(match.group(0), flush=True)  # Only the URL, no extra text
            break

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()

if __name__ == "__main__":
    main()
