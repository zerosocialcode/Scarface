<div align="center">
  <img src="https://raw.githubusercontent.com/zerosocialcode/Scarface/refs/heads/main/images/logo.png" alt="Scarface Logo" width="600">

  # Social Engineering & Credential Harvesting Automated Framework for Cyber Exercises

  > ⚠️ **Disclaimer**: This project is intended for educational and authorized penetration testing purposes only. Misuse of this tool for unauthorized access or attacks is strictly prohibited and illegal.

  *Actively maintained by [zerosocialcode](https://github.com/zerosocialcode)*
</div>

## 🔍 Overview

Scarface is a sophisticated phishing framework designed for penetration testing and security research. It provides a complete suite of tools to clone target websites, inject credential harvesting capabilities, deploy phishing servers, and capture credentials through various tunneling methods - all in a single integrated toolkit.

## ✨ Features

### Complete Phishing Lifecycle Management
- 📡 Website cloning with resource downloading  
- 📡 Automatic credential harvesting injection  
- 📡 Server deployment (PHP and Flask)  
- 📡 Real-time credential monitoring  
- 📡 Multiple tunneling options  

### Smart Injection System
- 📡 JavaScript injection for HTML sites  
- 📡 PHP code injection for PHP-based sites  
- 📡 Automatic backup of original files  
- 📡 Injection markers to prevent duplicates  

### Flexible Deployment
- 📡 Localhost testing  
- 📡 Cloudflared tunneling  
- 📡 Ngrok integration  
- 📡 LocalTunnel support  
- 📡 Mobile-responsive viewport injection  

### Credential Management
- 📡 Real-time monitoring  
- 📡 Desktop notifications  
- 📡 JSON storage format  
- 📡 Latest credential display  

## 🌐 Tunneling Options Comparison

| Feature         | Ngrok | Cloudflared | Localtunnel |
|----------------|-------|-------------|-------------|
| **Best for**   | Quick demos | Longer testing | Instant testing |
| **Setup**      | Easy | Moderate | Easiest |
| **Stability**  | 2hr limit | Very stable | Unstable |
| **Account**    | Required | Required | Not needed |

### Quick Decision Guide:
1. **Need it working right now?** → Localtunnel  
2. **Need to show someone for a few hours?** → Ngrok  
3. **Need it stable for days?** → Cloudflared  

[**How to install cloudflared, ngrok? →**](https://scarfaceframework.netlify.app/)

## 💉 Injection System
The framework includes an automated injection mechanism that:
- 📡 Adds credential capture functionality to cloned sites  
- 📡 Works with both static HTML and PHP sites  
- 📡 Preserves original site functionality  
- 📡 Stores captured data securely  
- 📡 Leaves minimal forensic traces  

All injections are designed to be:
- 🔄 Reversible (original files are backed up)  
- ⚖️ Ethical (includes usage warnings)  
- 🔍 Transparent (clearly visible in testing scenarios)  
## 🛠️ Usage
Clone the repository. and run this:
```
chmod +x setup.sh
./setup.sh
```
Run:
```
phish
```
1. Clone the target website using the built-in cloner  
2. Deploy the cloned site using your preferred tunneling method  
3. Monitor captured credentials through the dashboard  
4. Always ensure proper authorization before testing  

**Remember**: This tool should only be used on systems you own or have explicit permission to test.

## 🤝 Contribution
We welcome contributions from security professionals:
- 🐛 Report bugs or suggest features via Issues  
- 💡 Submit pull requests for improvements  
- 📖 Help improve documentation  
