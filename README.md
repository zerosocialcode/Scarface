# Social Engineering & Credential Harvesting Automated Framework for Cyber Exercises

## Overview
Scarface is a sophisticated phishing framework designed for penetration testing and security research. It provides a complete suite of tools to clone target websites, inject credential harvesting capabilities, deploy phishing servers, and capture credentials through various tunneling methods - all in a single integrated toolkit.
## Preview
![Scarface Preview](https://raw.githubusercontent.com/zerosocialcode/Scarface/refs/heads/main/images/temp.png)

## Features

- **Complete Phishing Lifecycle Management**:
  - Website cloning with resource downloading
  - Automatic credential harvesting injection
  - Server deployment (PHP and Flask)
  - Real-time credential monitoring
  - Multiple tunneling options

- **Smart Injection System**:
  - JavaScript injection for HTML sites
  - PHP code injection for PHP-based sites
  - Automatic backup of original files
  - Injection markers to prevent duplicates

- **Flexible Deployment**:
  - Localhost testing
  - Cloudflared tunneling
  - Ngrok integration
  - LocalTunnel support
  - Mobile-responsive viewport injection

- **Credential Management**:
  - Real-time monitoring
  - Desktop notifications
  - JSON storage format
  - Latest credential display

# Simple Guide to Tunneling Options

## Ngrok
- **Best for**: Quick demos and temporary testing
- **Setup**: Easiest (just download and run)
- **Works well**: For showing something quickly to a client
- **Downside**: Free version disconnects after 2 hours
- **Good to know**: You need to create an account first

## Cloudflared (Cloudflare Tunnel)
- **Best for**: More serious or longer testing
- **Setup**: A bit more involved but not too hard
- **Works well**: When you need something stable for days
- **Downside**: Requires installing the Cloudflared tool
- **Good to know**: No usage limits on free tier

## Localtunnel
- **Best for**: "I need this working in 30 seconds"
- **Setup**: Easiest (just run `npx localtunnel`)
- **Works well**: For super quick tests when alone
- **Downside**: Random URLs and sometimes drops connection
- **Good to know**: No account or installation needed

## Quick Decision Guide:
1. Need it working **right now**? → Localtunnel
2. Need to **show someone** for a few hours? → Ngrok
3. Need it **stable for days**? → Cloudflared

🔗 [How to install cloudflared, ngrok?](https://scarfaceframework.netlify.app/) - Complete installation guide

## Installation

```bash
https://github.com/zerosocialcode/Scarface.git
cd Scarface
pip install -r requirements.txt
