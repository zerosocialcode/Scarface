import os
import smtplib
import time
import sys
from email.message import EmailMessage
from pathlib import Path
from utils import ColorUtils, DisplayUtils

class EmailSender:
    def __init__(self):
        self.SMTP_SERVER = 'smtp.gmail.com'
        self.SMTP_PORT = 587
        self.SENDER_EMAIL = 'instagram.helpdesk.bot@gmail.com'
        self.SENDER_PASSWORD = 'nnqm rtnf vdsl gnsz'
        
        self.SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.PROJECT_ROOT = os.path.abspath(os.path.join(self.SCRIPT_DIR, '..', '..', '..'))
        
        self.MAILS_DIR = os.path.join(self.PROJECT_ROOT, 'data', 'mails')
        self.BANNER_PATH = os.path.join(self.PROJECT_ROOT, 'assets', 'banners', 'mailbird.txt')
        self.EMAILS_FILE = os.path.join(self.SCRIPT_DIR, 'emails.txt')
        
        self.display = DisplayUtils()
        self.colors = ColorUtils()
        
    def list_templates(self):
        templates_dir = Path(self.MAILS_DIR)
        if not templates_dir.exists():
            print(f"{self.colors.RED}[-] Templates directory not found: {self.MAILS_DIR}{self.colors.RESET}")
            return []
        
        templates = [f for f in templates_dir.iterdir() if f.suffix == '.html']
        print(f"\n{self.colors.BLUE}[*] Available templates:{self.colors.RESET}")
        for i, template in enumerate(templates):
            print(f"{self.colors.YELLOW}{i + 1}.{self.colors.RESET} {template.name}")
        return templates
    
    def get_template_content(self, template_path):
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"{self.colors.RED}[-] Error reading template: {e}{self.colors.RESET}")
            return None
    
    def send_email_logic(self, recipient, subject, html_content):
        msg = EmailMessage()
        msg['From'] = self.SENDER_EMAIL
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.set_content("This is a plain text fallback.")
        msg.add_alternative(html_content, subtype='html')
        
        try:
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(self.SENDER_EMAIL, self.SENDER_PASSWORD)
                smtp.send_message(msg)
                return True, None
        except Exception as e:
            return False, str(e)

    def get_user_input(self, prompt):
        try:
            return input(f"{self.colors.BLUE}[?]{self.colors.RESET} {prompt} ").strip()
        except EOFError:
            return ""

    def bulk_mode(self, delay):
        if not Path(self.EMAILS_FILE).exists():
            print(f"{self.colors.RED}[-] Error: {self.EMAILS_FILE} not found.{self.colors.RESET}")
            return

        with open(self.EMAILS_FILE, 'r') as f:
            recipients = [line.strip() for line in f if line.strip()]

        if not recipients:
            print(f"{self.colors.RED}[-] No emails found in file.{self.colors.RESET}")
            return

        print(f"\n{self.colors.BLUE}[*] Configuration{self.colors.RESET}")
        subject = self.get_user_input("Enter email subject:")
        if not subject: return

        templates = self.list_templates()
        if not templates: return
        
        try:
            choice_input = self.get_user_input(f"Choose template [1-{len(templates)}]:")
            if not choice_input: return
            choice = int(choice_input)
            selected_template = templates[choice - 1]
        except (ValueError, IndexError):
            print(f"{self.colors.RED}[-] Invalid template selection.{self.colors.RESET}")
            return

        html_content = self.get_template_content(selected_template)
        if not html_content: return

        print(f"\n{self.colors.BLUE}[*] Starting bulk operation for {len(recipients)} targets...{self.colors.RESET}\n")
        
        total = len(recipients)
        self.display.print_progress_bar(0, total, prefix='Sending:', suffix='')

        for i, recipient in enumerate(recipients):
            self.send_email_logic(recipient, subject, html_content)
            time.sleep(delay)
            self.display.print_progress_bar(i + 1, total, prefix='Sending:', suffix='')

        print(f"\n{self.colors.GREEN}[+] Bulk sending completed.{self.colors.RESET}")

    def single_mode(self):
        while True:
            print(f"\n{self.colors.BLUE}[*] Single Email Mode{self.colors.RESET}")
            recipient = self.get_user_input("Enter recipient email:")
            if not recipient: break

            subject = self.get_user_input("Enter email subject:")
            if not subject: break

            templates = self.list_templates()
            if not templates: break
            
            try:
                choice_input = self.get_user_input(f"Choose template [1-{len(templates)}]:")
                if not choice_input: continue
                choice = int(choice_input)
                selected_template = templates[choice - 1]
            except (ValueError, IndexError):
                print(f"{self.colors.RED}[-] Invalid template selection.{self.colors.RESET}")
                continue

            html_content = self.get_template_content(selected_template)
            if html_content:
                self.display.dynamic_print(f"Sending email to {recipient}...", self.colors.YELLOW)
                success, error = self.send_email_logic(recipient, subject, html_content)
                
                if success:
                    self.display.dynamic_print(f"Email sent successfully to {recipient}", self.colors.GREEN, end='\n')
                else:
                    self.display.dynamic_print(f"Failed to send to {recipient}: {error}", self.colors.RED, end='\n')

            cont = self.get_user_input("Send another email? (y/n):").lower()
            if cont != 'y':
                break

    def run(self):
        self.display.clear_screen()
        self.display.show_banner(self.BANNER_PATH, self.colors.BLUE)
        
        print(f"{self.colors.BOLD}1.{self.colors.RESET} Single Mode")
        print(f"{self.colors.BOLD}2.{self.colors.RESET} Bulk Mode")
        
        mode = self.get_user_input("Select Mode [1/2]:")

        if mode == '1':
            self.single_mode()
        elif mode == '2':
            try:
                delay_input = self.get_user_input("Enter delay between emails (seconds):")
                delay = float(delay_input) if delay_input else 0
            except ValueError:
                delay = 0
            self.bulk_mode(delay)
        else:
            if mode:
                print(f"{self.colors.RED}[-] Invalid mode selected.{self.colors.RESET}")

def main():
    try:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
            
        email_sender = EmailSender()
        email_sender.run()
    except KeyboardInterrupt:
        sys.stdout.write('\r')
        sys.stdout.flush()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    main()
