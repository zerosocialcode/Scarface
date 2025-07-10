import subprocess
import re
import sys

def main():
    proc = subprocess.Popen(
        ["ngrok", "http", "8080", "--log", "stdout"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    url_regex = re.compile(r"https://[a-zA-Z0-9\-]+\.ngrok\.io")
    while True:
        line = proc.stdout.readline()
        if not line:
            continue
        match = url_regex.search(line)
        if match:
            print(match.group(0), flush=True)
            break
    proc.wait()

if __name__ == "__main__":
    main()
