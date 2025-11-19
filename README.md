<div align="center">
  <img src="https://raw.githubusercontent.com/zerosocialcode/Scarface/refs/heads/main/images/logo.png" alt="Scarface Logo" width="600"/>
  <h1>Scarface Framework</h1>
  🛡️ Legal & Ethical Notice

This framework is a penetration testing toolkit for educational and authorized use only. Obtain explicit permission before running any phishing or credential-harvesting activities.

*Maintained by [zerosocialcode](https://t.me/zerosocialcode)*
</div>

---

## Overview

Scarface helps with phishing simulation and training by providing tools to:
- Clone webpages
- Capture submitted data
- Expose local services (Cloudflared / Ngrok)
- Build HTML email templates
- Send emails via SMTP

Use only in controlled, authorized environments.

## Requirements

- Cloudflared (or Ngrok)
- Python 3 and packages: beautifulsoup4, Flask, requests, termcolor
- Optional: pandas (for CSV-based recipient lists)

---

## Install (example)

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -O cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
cloudflared --version
```

Termux:
```bash
pkg install cloudflared
cloudflared --version
```

---

## Setup & Run

Make the setup script executable and run it:
```bash
chmod +x setup.sh
./setup.sh
```

Start the toolkit:
```bash
phish
```

---

## Modules

- Cloner — Create a replica of a web page for testing.
- Harvest — Host the cloned page and collect inputs. Use Cloudflared/Ngrok to get a public URL.
- Mailroom — Generate realistic HTML email templates (examples: Facebook, Instagram). Insert the Harvest public URL and export ready-to-send HTML files.
- MailBird — Send HTML emails via SMTP. Supports sending to one recipient or to many using a CSV list.

Workflow:
1. Clone a page and run Harvest.
2. Expose Harvest and copy the public URL.
3. Create an email in Mailroom embedding that URL.
4. Deliver the email with MailBird.

---

## MailBird — Gmail setup

1. Turn on 2-Step Verification for your Google account.
2. Create an App Password: Google Account → Security → App passwords.
3. Update MailBird main.py (EmailSender class):

```python
self.SENDER_EMAIL = 'your-email@gmail.com'           # your Gmail address
self.SENDER_PASSWORD = 'your-generated-app-password' # App Password
```

Notes:
- Use App Passwords when 2FA is enabled.
- Observe Gmail SMTP limits; use a transactional provider for high-volume testing.

---

## Example flow

1. Clone a target page.
2. Run Harvest and expose it.
3. Make an email in Mailroom with the exposed URL.
4. Send with MailBird to chosen recipients.

---

## Responsible use

Always have written authorization before testing. Use test accounts and isolated labs. The project owner is not responsible for misuse.

---

## Contributing

Templates, delivery improvements, and integrations are welcome. Open an issue or PR and include test files or logs.

---

## Support

If you need a tutorial or demo for Mailroom, MailBird, or the full workflow, contact: zerosocialcode@gmail.com or reach out on Telegram.

---
