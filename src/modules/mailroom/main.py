import os
import sys
import time
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, render_template_string, jsonify
import flask.cli

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
logging.getLogger('flask').setLevel(logging.ERROR)

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

flask.cli.show_server_banner = lambda *args: None

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
EMAIL_TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'data', 'email_templates')
SAVE_DIR = os.path.join(PROJECT_ROOT, 'data', 'mails')

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def get_available_templates():
    try:
        return sorted([
            f[:-5] for f in os.listdir(EMAIL_TEMPLATES_DIR)
            if f.endswith(".html") and not f.startswith("_")
        ])
    except FileNotFoundError:
        return []

def render_email(template_name, **data):
    template_file = os.path.join(EMAIL_TEMPLATES_DIR, f"{template_name}.html")
    if not os.path.exists(template_file):
        return f"<h1>Template {template_name} not found.</h1>"
    with open(template_file, 'r', encoding='utf-8') as tf:
        template_source = tf.read()
    return render_template_string(template_source, **data)

@app.route('/', methods=['GET', 'POST'])
def index():
    available_templates = get_available_templates()
    if not available_templates:
        return "<h1>No email templates found.</h1><p>Please add .html files to the data/email_templates directory.</p>"
    if request.method == 'POST':
        data = {field: request.form.get(field, '') for field in [
            'subject', 'greeting', 'body', 'closing', 'signature', 'footer',
            'button_text', 'button_url', 'logo_url', 'font',
            'header_color', 'body_color', 'footer_color', 'button_color',
            'header_text_color', 'footer_text_color', 'button_text_color', 'text_color',
            'hero_url', 'accent_color'
        ]}
        template_name = request.form.get('template_style', available_templates[0])
        generated_html = render_email(template_name, **data)
        session['generated_html'] = generated_html
        session['template_name'] = template_name
        return redirect(url_for('result'))
    return render_template("form.html", templates=available_templates)

@app.route('/result')
def result():
    generated_html = session.get('generated_html')
    template_name = session.get('template_name')
    if not generated_html:
        return redirect(url_for('index'))
    return render_template("result.html", generated_html=generated_html, template_name=template_name)

@app.route('/save_template', methods=['POST'])
def save_template():
    generated_html = session.get('generated_html')
    
    if not generated_html:
        return jsonify({"status": "error", "message": "No generated HTML found in session."}), 400

    if not os.path.exists(SAVE_DIR):
        try:
            os.makedirs(SAVE_DIR)
        except OSError as e:
            return jsonify({"status": "error", "message": f"Could not create directory: {e}"}), 500

    max_number = 0
    try:
        for f in os.listdir(SAVE_DIR):
            if f.startswith("email_") and f.endswith(".html"):
                try:
                    number_part = f[6:-5]
                    if number_part.isdigit():
                        num = int(number_part)
                        if num > max_number:
                            max_number = num
                except ValueError:
                    continue
    except OSError:
        pass

    next_number = max_number + 1
    filename = f"email_{next_number}.html"
    filepath = os.path.join(SAVE_DIR, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(generated_html)
        
        print(f"{Colors.GREEN}[Server] Saved backup to: {filepath}{Colors.END}")
        
        return jsonify({
            "status": "success", 
            "message": f"File saved as {filename}", 
            "path": filepath
        })
    except Exception as e:
        print(f"{Colors.RED}[Server] Error saving file: {e}{Colors.END}")
        return jsonify({"status": "error", "message": str(e)}), 500

def get_terminal_width():
    try:
        return os.get_terminal_size().columns
    except (OSError, AttributeError):
        return 80

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_banner():
    banner_path = os.path.join(PROJECT_ROOT, 'assets', 'banners', 'mailroom.txt')
    try:
        with open(banner_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return f"{Colors.BLUE}Email Template Generator{Colors.END}"

def print_banner():
    banner_text = load_banner()
    for line in banner_text.split('\n'):
        if line.strip():
            print(f"{Colors.BLUE}{line}{Colors.END}")
    print()

def print_server_info():
    width = min(get_terminal_width(), 80) - 20
    separator = '─' * width
    
    print(f"{Colors.BOLD}Server Status{Colors.END}")
    print(f"{separator}")
    print(f"Local URL:     {Colors.BOLD}{Colors.GREEN}http://127.0.0.1:5000{Colors.END}")
    print(f"Save Path:     {Colors.BOLD}{Colors.YELLOW}{SAVE_DIR}{Colors.END}")
    print()

def print_template_info():
    width = min(get_terminal_width(), 80) - 20
    separator = '─' * width
    templates = get_available_templates()
    
    print(f"{Colors.BOLD}Template Library{Colors.END}")
    print(f"{separator}")
    print(f"Available Templates: {Colors.BOLD}{Colors.GREEN}{len(templates)}{Colors.END}")
    
    if templates:
        template_preview = ', '.join(templates[:3])
        if len(templates) > 3:
            template_preview += f"... (+{len(templates)-3} more)"
        
        max_template_width = width - 25
        if len(template_preview) > max_template_width:
            template_preview = template_preview[:max_template_width-3] + "..."
            
        print(f"Template Names: {template_preview}")
    print()

def print_instructions():
    print(f"{Colors.BOLD}Quick Start{Colors.END}")
    print(f"{'─' * (min(get_terminal_width(), 80) - 20)}")
    
    instructions = [
        f"{Colors.GREEN}•{Colors.END} Open your browser and go to the URL above",
        f"{Colors.GREEN}•{Colors.END} Create email templates using the web interface",
        f"{Colors.GREEN}•{Colors.END} Click 'Download HTML' to save locally AND to server",
    ]
    
    for instruction in instructions:
        print(instruction)
    print()

def print_footer():
    width = min(get_terminal_width(), 80) - 20
    print(f"{'─' * width}")
    
    commands = [
        f"{Colors.YELLOW}Ctrl+C{Colors.END} to stop server",
        f"{Colors.YELLOW}F5{Colors.END} to refresh browser"
    ]
    
    print(f"Commands: {' │ '.join(commands)}")
    print(f"\n{'=' * min(width + 20, 80)}")
    print(f"Server is running...\n")

def show_loading(duration=2):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    
    print(f"Starting server... ", end="", flush=True)
    
    while time.time() < end_time:
        for frame in frames:
            if time.time() >= end_time:
                break
            print(f"\b{frame}", end="", flush=True)
            time.sleep(0.1)
    
    print(f"\b{Colors.GREEN}✓{Colors.END}")

def show_interface():
    clear_screen()
    print_banner()
    show_loading()
    print()
    print_server_info()
    print_template_info()
    print_instructions()
    print_footer()

if __name__ == '__main__':
    try:
        show_interface()
        if 'WERKZEUG_SERVER_FD' in os.environ:
            del os.environ['WERKZEUG_SERVER_FD']
        
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BLUE}Server stopped{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error starting server: {e}{Colors.END}")
        sys.exit(1)
