![Scarface Preview](https://raw.githubusercontent.com/zerosocialcode/Scarface/refs/heads/main/images/logo.png)

<div align="center">

> ⚠️ **Disclaimer**: This project is intended for educational and authorized penetration testing purposes only. Misuse of this tool for unauthorized access or attacks is strictly prohibited and illegal.

</div>

<div align="center">

# Social Engineering & Credential Harvesting Automated Framework for Cyber Exercises

</div>

<div align="center">

> **Actively maintained by [zerosocialcode](https://github.com/zerosocialcode)**

</div>
<div align="center">

>

</div>

<div align="center">

## Overview

</div>

<div align="center">

Scarface is a sophisticated phishing framework designed for penetration testing and security research. It provides a complete suite of tools to clone target websites, inject credential harvesting capabilities, deploy phishing servers, and capture credentials through various tunneling methods - all in a single integrated toolkit.

</div>

<div align="center">

## Features

</div>

<div align="center">

- **Complete Phishing Lifecycle Management**:

</div>
<div align="center">

  - Website cloning with resource downloading

</div>
<div align="center">

  - Automatic credential harvesting injection

</div>
<div align="center">

  - Server deployment (PHP and Flask)

</div>
<div align="center">

  - Real-time credential monitoring

</div>
<div align="center">

  - Multiple tunneling options

</div>

<div align="center">

- **Smart Injection System**:

</div>
<div align="center">

  - JavaScript injection for HTML sites

</div>
<div align="center">

  - PHP code injection for PHP-based sites

</div>
<div align="center">

  - Automatic backup of original files

</div>
<div align="center">

  - Injection markers to prevent duplicates

</div>

<div align="center">

- **Flexible Deployment**:

</div>
<div align="center">

  - Localhost testing

</div>
<div align="center">

  - Cloudflared tunneling

</div>
<div align="center">

  - Ngrok integration

</div>
<div align="center">

  - LocalTunnel support

</div>
<div align="center">

  - Mobile-responsive viewport injection

</div>

<div align="center">

- **Credential Management**:

</div>
<div align="center">

  - Real-time monitoring

</div>
<div align="center">

  - Desktop notifications

</div>
<div align="center">

  - JSON storage format

</div>
<div align="center">

  - Latest credential display

</div>

<div align="center">

# Simple Guide to Tunneling Options

</div>

<div align="center">

## Ngrok

</div>

<div align="center">

- **Best for**: Quick demos and temporary testing

</div>
<div align="center">

- **Setup**: Easiest (just download and run)

</div>
<div align="center">

- **Works well**: For showing something quickly to a client

</div>
<div align="center">

- **Downside**: Free version disconnects after 2 hours

</div>
<div align="center">

- **Good to know**: You need to create an account first

</div>

<div align="center">

## Cloudflared (Cloudflare Tunnel)

</div>

<div align="center">

- **Best for**: More serious or longer testing

</div>
<div align="center">

- **Setup**: A bit more involved but not too hard

</div>
<div align="center">

- **Works well**: When you need something stable for days

</div>
<div align="center">

- **Downside**: Requires installing the Cloudflared tool

</div>
<div align="center">

- **Good to know**: No usage limits on free tier

</div>

<div align="center">

## Localtunnel

</div>

<div align="center">

- **Best for**: "I need this working in 30 seconds"

</div>
<div align="center">

- **Setup**: Easiest (just run `npx localtunnel`)

</div>
<div align="center">

- **Works well**: For super quick tests when alone

</div>
<div align="center">

- **Downside**: Random URLs and sometimes drops connection

</div>
<div align="center">

- **Good to know**: No account or installation needed

</div>

<div align="center">

## Quick Decision Guide:

</div>

<div align="center">

1. Need it working **right now**? → Localtunnel  

</div>
<div align="center">

2. Need to **show someone** for a few hours? → Ngrok  

</div>
<div align="center">

3. Need it **stable for days**? → Cloudflared

</div>

<a href="https://scarfaceframework.netlify.app/" style="color: #2e86c1; text-decoration: none; font-weight: bold;">How to install cloudflared, ngrok? →</a>

<div align="center">

## Injection System

</div>

<div align="center">

The framework includes an automated injection mechanism that:

</div>

<div align="center">

- Adds credential capture functionality to cloned sites

</div>
<div align="center">

- Works with both static HTML and PHP sites

</div>
<div align="center">

- Preserves original site functionality

</div>
<div align="center">

- Stores captured data securely

</div>
<div align="center">

- Leaves minimal forensic traces

</div>

<div align="center">

All injections are designed to be:

</div>
<div align="center">

- Reversible (original files are backed up)

</div>
<div align="center">

- Ethical (includes usage warnings)

</div>
<div align="center">

- Transparent (clearly visible in testing scenarios)

</div>

<div align="center">

## Usage

</div>

<div align="center">

Scarface is designed for authorized security testing and educational purposes. To use the framework:

</div>

<div align="center">

1. Clone the target website using the built-in cloner  

</div>
<div align="center">

2. Deploy the cloned site using your preferred tunneling method  

</div>
<div align="center">

3. Monitor captured credentials through the dashboard  

</div>
<div align="center">

4. Always ensure proper authorization before testing

</div>

<div align="center">

**Remember**: This tool should only be used on systems you own or have explicit permission to test.

</div>

<div align="center">

## Contribution

</div>

<div align="center">

We welcome contributions from security professionals:

</div>

<div align="center">

- Report bugs or suggest features via Issues

</div>
<div align="center">

- Submit pull requests for improvements

</div>
<div align="center">

- Help improve documentation

</div>

<div align="center">

## Structure

</div>

![Structure](https://raw.githubusercontent.com/zerosocialcode/Scarface/refs/heads/main/images/structure.png)

<div align="center">

## Connect

</div>

<p align="left">
  <a href="https://t.me/zerosocialcode" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram" height="45"/>
  </a>
</p>