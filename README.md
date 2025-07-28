<div align="center">
  <img src="https://raw.githubusercontent.com/zerosocialcode/Scarface/refs/heads/main/images/logo.png" alt="Scarface Logo" width="600"/>

  <h1>Scarface Framework</h1>
  🛡️ Legal & Ethical Notice

This framework is a **penetration testing tool** designed for **educational** use and **authorized environments only**.
Any misuse is the sole responsibility of the user. Always follow legal and ethical guidelines.


*Maintained by [zerosocialcode](https://github.com/zerosocialcode)*

</div>

---

## 🚀 What is Scarface?

**Scarface** is an all-in-one phishing and credential harvesting framework built for ethical hacking and cybersecurity simulations. It enables professionals to:

* Clone real-world websites
* Inject harvesting scripts
* Host phishing servers
* Capture credentials
* Use tunneling services to expose local services

Whether you're running red-team engagements, training simulations, or lab testing, Scarface automates the full phishing lifecycle.

## Requirements

Ensure the following packages and tools are installed:

- `Cloudflared`
- `Ngrok`
- `beautifulsoup4`
- `Flask`
- `requests`
- `termcolor`

---

## Installation

### Cloudflared

### Other:
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -O cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

Verify installation:
```bash
cloudflared --version
```

#### Termux:
```bash
pkg install cloudflared
```

Verify installation:
```bash
cloudflared --version
```

---

## Setup

Make the setup script executable:
```bash
chmod +x setup.sh
```

Then run:
```bash
./setup.sh
```

---

## Run

Start the toolkit using:
```bash
phish
```

---

## Usage

The toolkit offers the following modules:

1. **Cloner Module**  
   Clone any web page for phishing simulation.

2. **Harvest Module**  
   Harvest credentials entered by targets on cloned sites.
