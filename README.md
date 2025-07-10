# Scarface

> This project is provided strictly for educational and authorized security testing purposes only. Use responsibly and only on systems you have explicit permission to assess.

---

## Preview

![Scarface Preview](https://raw.githubusercontent.com/zerosocialcode/Scarface/refs/heads/main/.prvw.png)

---

## Overview

**Scarface** is a modular penetration testing and social engineering framework. It enables security professionals and researchers to clone websites, harvest credentials, and expose phishing pages securely to the internet. The framework is designed for flexibility, automation, and ease of use, allowing you to manage campaigns, payloads, and supporting tools from a single, universal platform.

---

## Features

- **Universal Launcher:** Manage and launch any module or tool in the framework from a single interface.
- **Site Cloning:** Clone target login pages using advanced Python and wget-based engines.
- **Harvesting:** Serve cloned sites and automatically log credentials in organized JSON files.
- **Exposure:** Expose local servers to the internet using Cloudflared, Ngrok, or LocalTunnel with ready-to-use scripts.
- **Multi-Module Support:** Easily add or remove modules and campaigns by managing subfolders.
- **Cross-Platform:** Compatible with Linux, macOS, and Windows (Python 3.x).
- **Custom Branding:** Supports a project banner via `.banner.txt`.

---

## Directory Structure

```
Scarface/
├── main.py                 # Universal launcher
├── Harvest/                # Main harvesting server & logic
│   ├── main.py
│   └── sites/
├── Scarface-Cloner/        # Website cloner engine
│   └── main.py
├── expose/                 # Public exposure/tunneling scripts
│   ├── cloudflared.py
│   ├── localtunnel.py
│   └── ngrok.py
├── credentials/            # Harvested credentials (per site)
│   └── Facebook/
│       └── result.json
├── sites/                  # Cloned phishing sites
│   └── Facebook/
│       └── index.html
└── .banner.txt             # (Optional) Banner for branding
```

---

## Usage

1. **Setup**
    - Ensure Python 3.x is installed.
    - Install dependencies for each module (such as Flask, BeautifulSoup, requests) as needed.
    - Place your own tools or modules as subfolders; each should include a `main.py` or `__main__.py` file.

2. **Launching Scarface**
    ```bash
    python3 main.py
    ```
    - The launcher lists all detected modules.
    - Select a module (e.g., Harvest or Scarface-Cloner) to run the server or clone a new site.

3. **Cloning & Harvesting**
    - Use Scarface-Cloner to capture a target website (e.g., Facebook). The cloned site appears in `/sites/Facebook/`.
    - Use Harvest to serve the cloned site and collect credentials.
    - Use a script from `/expose/` to tunnel your local server for remote access.

4. **Reviewing Captured Data**
    - Credentials are saved as JSON in `/credentials/[SiteName]/result.json`.

---

## Example Workflow

1. **Clone a site:**  
   Run Scarface-Cloner to create a clone (e.g., Facebook).
2. **Serve the cloned site:**  
   Launch Harvest to serve the site and capture data.
3. **Expose to internet:**  
   Use a script in `/expose/` (like `cloudflared.py`) to provide a public URL.
4. **Collect credentials:**  
   Harvested data is stored in `/credentials/[SiteName]/`.

---

## Disclaimer

This project is intended strictly for educational and authorized security research. The author assumes no responsibility for misuse.

---

**Developer:** zerosocialcode  
[GitHub](https://github.com/zerosocialcode)  
[Facebook](https://facebook.com/zerosocialcode)  
Email: zerosocialcode@gmail.com

```
