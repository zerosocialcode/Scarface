<div align="center">
  <img src="https://raw.githubusercontent.com/zerosocialcode/Scarface/refs/heads/main/images/logo.png" alt="Scarface Logo" width="600"/>

  <h1>Scarface Framework</h1>
  <h3>🎯 Automated Social Engineering & Credential Harvesting Toolkit for Cybersecurity Exercises</h3>

> ⚠️ **Disclaimer:** This tool is intended strictly for **authorized penetration testing and educational purposes**. Unauthorized use is illegal and strictly prohibited.

*Maintained by [@zerosocialcode](https://github.com/zerosocialcode)*

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

---

## ✨ Key Features

### 🔁 Phishing Lifecycle Automation

* 🌐 One-click website cloning
* 💉 Credential harvester auto-injection
* 🔧 Flask & PHP phishing server setup
* 👁️ Real-time credential monitoring
* 🌍 Multiple tunneling integrations

### 💉 Smart Injection System

* 🧠 JavaScript injection for HTML targets
* 💘 PHP injection for dynamic sites
* 📀 Automatic backup of original site files
* 🔐 Duplicate-safe injection markers

### 🚀 Deployment Options

* 🧪 Localhost testing
* ☁️ Cloudflared
* 🕳️ Ngrok
* 🔓 LocalTunnel
* 📱 Mobile-responsive injection layouts

### 📋 Credential Management

* 🔍 Live capture display
* 🔔 Desktop notifications
* 📁 JSON format storage
* ⏱️ Latest credentials always visible

---

## 🌐 Tunneling Services: Quick Comparison

| Feature            | **Ngrok**   | **Cloudflared**    | **LocalTunnel** |
| ------------------ | ----------- | ------------------ | --------------- |
| **Best for**       | Short demos | Long-term sessions | Instant use     |
| **Setup**          | Easy        | Moderate           | Easiest         |
| **Stability**      | \~2hr limit | Very stable        | Less stable     |
| **Account Needed** | ✅ Yes       | ✅ Yes              | ❌ No            |

### 🔍 Recommendation:

* 🕒 **Immediate testing?** → Use **LocalTunnel**
* 👥 **Demo for a few hours?** → Use **Ngrok**
* 🧱 **Need stability over time?** → Use **Cloudflared**
---

## 💉 Injection Engine Explained

Scarface’s injection module automatically integrates credential capture into cloned pages without breaking original functionality.

* 🖠️ Supports both **HTML** and **PHP** targets
* 🔐 Injects stealthy credential harvesters
* 🔁 Backs up all original files
* 🧼 Minimal forensic trace footprint
* 🧪 Ideal for controlled environments and testing scenarios

All injections are:

* ✅ Reversible
* ⚠️ Transparent for training
* ✔️ Safe within authorized boundaries

---

## 🛠️ Getting Started

Clone the repository and install:

```bash
chmod +x setup.sh
./setup.sh
```

Run the tool:

```bash
phish
```

### Step-by-step Workflow:

1. 🧲 Clone a target website
2. 💉 Inject the harvesting code
3. 🚀 Deploy using your chosen tunnel
4. 🔍 Monitor credentials live

> ⚠️ **Important:** Always have **explicit permission** before conducting any tests.

---

## 🤝 Contributing

Contributions are welcomed from cybersecurity professionals and enthusiasts:

* 🐞 Report bugs or request features via [Issues](https://github.com/zerosocialcode/Scarface/issues)
* ⚙️ Submit pull requests for improvements
* 📘 Help enhance the documentation

---

## 🛡️ Legal & Ethical Notice

This framework is a **penetration testing tool** designed for **educational** use and **authorized environments only**.
Any misuse is the sole responsibility of the user. Always follow legal and ethical guidelines.

---

<div align="center">
  Author: <a href="https://github.com/zerosocialcode">zerosocialcode</a>
</div>
