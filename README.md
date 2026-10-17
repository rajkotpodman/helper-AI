<div align="center">

# ⚡ Helper-AI
### The Autonomous AI Agent with Full PC & Internet Control
**Run anything on your computer, automate the web, and solve complex tasks simply by typing what you want in plain human language.**

*Give Helper-AI a goal. It creates a plan, inspects and reverse-engineers any application, remembers its controls forever, runs tools, self-heals around errors, and delivers 100% completed results—without endless questions.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI/CD Pipeline](https://github.com/rajkotpodman/helper-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/rajkotpodman/helper-AI/actions/workflows/ci.yml)
[![Docker Build](https://github.com/rajkotpodman/helper-AI/actions/workflows/docker-build.yml/badge.svg)](https://github.com/rajkotpodman/helper-AI/actions/workflows/docker-build.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![Tests: 175+ Passed](https://img.shields.io/badge/tests-175%2B%20passed-success.svg)]()

<br>

[📖 Non-Technical User Manual](HOW_TO_USE.md) • [🇮🇳 ગુજરાતી માર્ગદર્શિકા (Gujarati Guide)](HOW_TO_USE.md#-%E0%AA%97%E0%AB%81%E0%AA%9C%E0%AA%B0%E0%AA%BE%E0%AA%A4%E0%AB%80-%E0%AA%B5%E0%AA%BF%E0%AA%AD%E0%AA%BE%E0%AA%97-gujarati-section) • [🛡️ Security Toolkit](security_toolkit/README.md) • [📋 Changelog](CHANGELOG.md)

</div>

---

## 🌟 What is Helper-AI? (Explained Simply for Everyone)

Imagine having a smart, tireless personal assistant sitting next to your computer. Normal chatbots (like ChatGPT or Claude) can only chat and write text on screen. **Helper-AI actually does the work for you on your computer**:

* 📁 **Organizes your messy computer:** Finds scattered files across your Downloads or Desktop and neatly groups them into labeled folders.
* 🧩 **Understands and Operates Any Software (REA):** Uses Reverse Engineering to understand how apps (Notepad, Calculator, VS Code, Spotify, Slack, or any website) work from the inside out, maps their buttons and hotkeys, and saves them to memory forever!
* ⚡ **100% Accurate & Lightning Fast:** Never relies on slow, clumsy mouse wandering. Once an app is remembered, it operates it using instant verified keyboard hotkeys and direct automation handles.
* 🔍 **Researches the web and writes reports:** Reads articles online, downloads images or PDFs, and compiles clean, formatted reports directly onto your Desktop.
* 💻 **Monitors your computer's health:** Checks how much RAM, CPU, or hard drive space you have left, and safely closes frozen programs.
* 🌐 **Automates social media & websites:** Logs into your browser, drafts and publishes posts on LinkedIn, Facebook, or Blogger, and fills out forms.
* 🛡️ **Defends your PC:** Performs defensive security audits, scans open network ports, and alerts you if sensitive system files have been altered.
* 🗣️ **Speaks aloud in 30+ languages:** Can read answers aloud to you in natural human voices.
* 🧠 **Persistent Memory Log:** Never forgets your instructions or learned applications, remembering them across restarts.

---

## ⚡ The 3-Minute Beginner Quickstart (No Technical Skills Needed!)

You don't need any programming, coding, or computer science knowledge. Follow these 4 easy steps:

### Step 1: Install Python (Takes 1 Minute)
If you don't already have Python installed:
1. Visit the official Python download page: **[https://www.python.org/downloads/](https://www.python.org/downloads/)**
2. Download and run the installer for your computer.
3. ⚠️ **VERY IMPORTANT STEP:** On the very first screen of the installer, check the small box at the bottom that says **"Add python.exe to PATH"**.
4. Click **Install Now**.

### Step 2: Download Helper-AI
1. Click the green **Code** button at the top of this GitHub repository and click **Download ZIP**.
2. Extract the unzipped folder anywhere on your computer (for example, on your `Desktop` or `C:\` drive).

### Step 3: Start Helper-AI in 1 Click
* **On Windows:** Open the folder and **double-click `run.bat` or `start.bat`**.
* **On Linux or Mac:** Open a terminal in the folder and type:
  ```bash
  python app.py
  ```

### Step 4: Use the Web Dashboard
A black command window will start for a few seconds, and your default web browser will automatically open up at:
👉 **`http://localhost:8000`**

You will see the dark-themed control center. Simply type what you want in plain English or speak into your microphone, then click **🚀 Execute Goal**!

---

## 🖥️ What the Web Dashboard Looks Like

```text
+-------------------------------------------------------------------------------------------------+
| ⚡ Helper-AI               [● PC Control Online]  [🧩 Memory (0.02 MB)]  [⚙️ Settings]  [🛡️ Safe Mode] |
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|   🎯 What goal would you like Helper-AI to achieve?                                             |
|   +-----------------------------------------------------------------------------------------+   |
|   | Type your goal here in plain human language... (e.g. "Clean up my Downloads folder")   |   |
|   +-----------------------------------------------------------------------------------------+   |
|                                                                                                 |
|   Quick Action Ideas:                                                                           |
|   [💻 Check PC Health]  [🔍 Research AI & Save Report]  [📂 Clean Downloads Folder]             |
|   [🧩 Reverse Engineer Notepad]  [🌐 List GitHub Repos]  [📝 Publish Social Media Post]         |
|                                                                                                 |
|   Status: Ready (RuleEngine Offline Mode Active)                 [⏹ Stop Agent] [🚀 Execute Goal]|
+-------------------------------------------------------------------------------------------------+
| 📊 Real-Time Execution Feed                                                                     |
|   Step 0: ⚡ Loaded AI-friendly memory for 'Notepad'. Hotkeys (Ctrl+S, Ctrl+N) ready.           |
|   Step 1: 💭 Thought: "Opening Notepad and writing text using 100% accurate fast path..."       |
|           ⚡ Action: fast_app_operate(target="Notepad", action="save")                          |
|           📋 Result: Executed fast-path 'save' (ctrl+s) on 'Notepad' with 100% precision.       |
|   🎉 MISSION ACCOMPLISHED! Goal executed successfully.                                          |
+-------------------------------------------------------------------------------------------------+
```

---

## 🧩 REA: Reverse Engineer Anything & AI App Memory Store

One of Helper-AI's most revolutionary capabilities is its integration with **REA (Reverse Engineer Anything)** and its **Persistent App Knowledge Memory Store**:

### How It Works:
1. **The Problem with Traditional AI Agents:** Standard AI agents try to click buttons by guessing where they are from a screenshot. If a window moves, or a button color changes, the agent gets confused and fails.
2. **Helper-AI's Solution:** When Helper-AI encounters any application (Notepad, Calculator, VS Code, Spotify, Slack, or any web application), it **reverse-engineers** it:
   - **X-Rays the Application:** Scans the internal UI Automation tree, controls (buttons, menus, text boxes), and keyboard shortcuts.
   - **Saves App Memory Forever:** Stores an AI-friendly profile in `agent_memory/apps/<app_slug>.json` and records it in `agent_memory.md`.
   - **100% Fast-Path Execution:** The next time you ask Helper-AI to do anything in that app, it doesn't wander around the screen. It immediately retrieves the remembered hotkeys (like `Ctrl+S`, `Ctrl+O`, `Ctrl+N`) and direct Automation IDs, executing the task in **one step with 100% accuracy and zero delay!**

### Pre-Seeded Essential Applications:
Helper-AI comes pre-loaded with fast-path memory profiles for common software:
* 📝 **Notepad (`notepad.exe`):** Fast hotkeys for Save (`Ctrl+S`), Open (`Ctrl+O`), New (`Ctrl+N`), Find (`Ctrl+F`), and text controls.
* 🧮 **Calculator (`CalculatorApp.exe`):** Direct calculation triggers, number entry, clear (`Esc`), and equals (`Enter`).
* 💻 **Visual Studio Code (`code.exe`):** Command Palette (`Ctrl+Shift+P`), Quick Open (`Ctrl+P`), Save (`Ctrl+S`), and terminal toggle.
* 🌐 **Google Chrome (`chrome.exe`):** Address bar focus (`Ctrl+L`), New Tab (`Ctrl+T`), Close Tab (`Ctrl+W`), and history.
* 🧭 **Microsoft Edge (`msedge.exe`):** Address bar focus (`Ctrl+L`), Tabs, and Favorites.
* 📁 **File Explorer (`explorer.exe`):** Address bar jump (`Alt+D`), New Folder (`Ctrl+Shift+N`), and rename (`F2`).

### Reverse-Engineering Any Custom App:
Want Helper-AI to understand a new application or website?
* Simply type: `"Reverse engineer Spotify, map its controls, and save to memory"`
* Or open the **Memory** modal on the web dashboard, type the app name in the **"Analyze"** box, and click **Analyze**!

---

## 💡 Practical Examples of What You Can Tell Helper-AI

Here are real tasks you can copy and paste into Helper-AI right now:

### 🧩 1. Reverse Engineering & App Operation
* `"Reverse engineer Notepad, extract its UI automation controls, and save it to app memory."`
* `"Check app memory for Calculator and use its fast path to calculate 128 * 4."`
* `"Open VS Code and use its command palette hotkey from memory."`
* `"Analyze the web app https://news.ycombinator.com and remember its navigation structure."`

### 📁 2. File & Computer Organization
* `"Look at my Downloads folder, create subfolders for 'Images', 'Documents', and 'Installers', and move the files into them."`
* `"Find all files larger than 100 MB on my C: drive and save a list to Desktop/large_files.txt."`
* `"Search for all files ending with .log in my project folder and delete them."`

### 💻 3. Computer Health & Performance
* `"Check my PC health: how much CPU and RAM am I using? Save a summary to Desktop/health.txt."`
* `"Check if any process is using more than 70% CPU and list them."`
* `"Safely close the application using port 8000 so I can free it up."`

### 🌐 4. Web Research & Reports
* `"Search the internet for the top 5 artificial intelligence news stories this week and save a detailed report to Desktop/ai_news.md."`
* `"Fetch the text of the webpage https://example.com and summarize it in 10 bullet points."`
* `"Download the latest Docker cheat sheet and save it to my Downloads folder."`

### 📱 5. Social Media & Content Publishing
* `"Draft an informative LinkedIn post about autonomous AI agents and publish it to my feed."`
* `"Create a Facebook post summarizing our newest product launch and publish it."`
* `"Write a 5-paragraph blog post about Python automation tips and publish it to Blogger."`

### 🛡️ 6. Defensive Security & Auditing
* `"Run a defensive security audit on my computer and check which network ports are open."`
* `"Audit the web security headers of http://localhost:8000 and give me a scorecard."`
* `"Create a cryptographic baseline of my project directory so I know if any file gets tampered with."`

---

## 🧰 Complete Arsenal: All 36 Registered Tools

Helper-AI comes built-in with **36 specialized tools**. The agent automatically selects the right tool for each step:

| # | Tool Name | Category | What It Does (Simple Explanation) |
| :-: | :--- | :--- | :--- |
| 1 | **`reverse_engineer_app`** | REA / Memory | Dissects any application, window, binary, or website, mapping controls and saving them to memory. |
| 2 | **`query_app_memory`** | REA / Memory | Instantly retrieves pre-digested fast-paths, hotkeys, and Automation IDs for known applications. |
| 3 | **`fast_app_operate`** | REA / Speed | Controls apps with 100% accuracy using verified hotkeys or direct UI Automation without delay. |
| 4 | **`mcp_rea_call`** | REA / Advanced | Calls any of the 200+ specialized reverse-engineering tools from the connected REA engine. |
| 5 | **`universal_terminal`** | System | Runs any terminal or PowerShell command on Windows, Linux, or Mac; supports heavy background tasks. |
| 6 | **`synthesize_os_command`** | System | Translates plain English intentions into exact, safe commands for your specific operating system. |
| 7 | **`command_hub`** | System | Downloads, searches, and caches community command cheat sheets (from cheat.sh and encyclopedia). |
| 8 | **`audit_security_baseline`** | Security | Audits open network ports, firewall status, security patches, and system hardening posture. |
| 9 | **`deep_web_crawl`** | Web | Recursively crawls websites and documentation portals into full, structured markdown knowledge files. |
| 10 | **`batch_fetch_web`** | Web | Concurrently downloads and extracts multiple web pages in parallel. |
| 11 | **`fetch_github_repo`** | Web | Inspects any GitHub repository, fetching files, folder trees, README, releases, and codebases. |
| 12 | **`fetch_web_content`** | Web | Extracts clean, readable article text from any web address without ads or clutter. |
| 13 | **`duckduckgo_search`** | Web | Searches the live internet for answers without needing any paid search API keys. |
| 14 | **`download_file`** | Web | Downloads files or documents directly from the internet onto your computer. |
| 15 | **`execute_python_code`** | Code | Runs Python scripts in an isolated sandbox with automatic dependency installation. |
| 16 | **`build_project_files`** | Code | Scaffolds and writes entire multi-file software projects and folder trees in 1 step. |
| 17 | **`execute_powershell`** | System | Executes native PowerShell scripts with automatic quoting for paths with spaces. |
| 18 | **`read_file`** | Files | Reads and inspects the contents of text, code, or configuration files. |
| 19 | **`write_file`** | Files | Creates new files or overwrites existing files with clean text. |
| 20 | **`list_directory`** | Files | Lists all files, folders, and sizes inside any directory (e.g. Desktop, Downloads). |
| 21 | **`search_files`** | Files | Searches for files by name, extension, or keyword across your drives. |
| 22 | **`move_or_copy_file`** | Files | Renames, moves, or makes duplicates of files and folders safely. |
| 23 | **`process_manager`** | System | Lists running programs and safely terminates frozen or unresponsive processes. |
| 24 | **`system_health`** | System | Checks CPU load, RAM usage, hard drive capacity, and computer uptime. |
| 25 | **`open_application`** | Apps | Opens desktop applications like Edge, Chrome, Notepad, Calculator, or Spotify. |
| 26 | **`manage_ollama`** | AI | Pulls, runs, and lists local AI models so you can run Helper-AI 100% offline. |
| 27 | **`check_connections`** | Network | Checks internet, Google Translate, Chrome port 9222, and API status with zero hassle. |
| 28 | **`browser_automation`** | Browser | Controls the dedicated browser to log in, navigate, click, fill forms, and post on social media. |
| 29 | **`desktop_gui_control`** | GUI | Simulates human mouse clicks, keyboard typing, hotkeys (`Ctrl+C`, `Win+R`), and window management. |
| 30 | **`text_to_speech`** | Voice | Speaks answers aloud using Microsoft's neural voice engine across dozens of natural accents. |
| 31 | **`vision_browser`** | Vision | Takes high-resolution screenshots and captures webpage visual layout using Playwright. |
| 32 | **`mcp_tool`** | Extensibility| Connects to external Model Context Protocol (MCP) servers to add new third-party tools. |
| 33 | **`deep_research_studio`** | Superpower | Multi-query search expansion, parallel distillation, and executive intelligence dossier synthesis. |
| 34 | **`orchestrate_complex_goal`**| Superpower | Structures massive tasks into 5-phase execution pipelines. |
| 35 | **`code_studio_builder`** | Superpower | Builds multi-file projects in 1 step with automated AST syntax checking and verification. |
| 36 | **`system_super_optimizer`** | Superpower | Introspective PC diagnostics, memory optimization analysis, and junk file scanning. |

---

## ⚙️ AI Models & Free Offline Mode

Helper-AI works with **any AI provider** you prefer:

| Mode / Provider | Internet Needed? | Cost | How to Use |
| :--- | :---: | :---: | :--- |
| **Smart Rule Engine** *(Built-in)* | ❌ No | **100% Free** | Default out-of-the-box mode! No API keys or credit card needed. |
| **Google Gemini** | ✅ Yes | **Free Tier Available** | Get a free key at [Google AI Studio](https://aistudio.google.com/), add `GEMINI_API_KEY` in `.env`. |
| **Ollama Local AI** | ❌ No | **100% Free** | Install [Ollama](https://ollama.com/), run `ollama pull qwen2.5:1.5b`. Works 100% private on your machine. |
| **OpenAI (GPT-4o)** | ✅ Yes | Paid API | Add `OPENAI_API_KEY` in `.env`. |
| **Groq (Ultra-Fast)** | ✅ Yes | Free Tier Available | Add `GROQ_API_KEY` in `.env`. |

### How to configure your AI key (Optional):
1. Rename or copy `.env.example` to `.env`.
2. Open `.env` in Notepad and set:
   ```ini
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_actual_key_here
   ```
3. Save the file. That's it!

---

## 🛡️ Safe Mode & 1-Click Approvals (Human-in-the-Loop)

You never have to worry about the agent doing something destructive:
- **Destructive Action Blocker:** In Safe Mode (`SAFE_MODE=true`), commands that format disks or wipe system folders are automatically blocked before they can ever run.
- **1-Click Approvals:** If Helper-AI is about to publish a post on social media or delete a file, it pauses and shows a friendly approval pop-up on your screen asking:  
  *`"Helper-AI wants to publish this LinkedIn post. Do you approve? [Yes] / [No]"`*
- You remain in complete control at all times!

---

## ❓ Frequently Asked Questions (FAQ) for Beginners

### Q1: Is Helper-AI free?
**Yes!** Helper-AI is 100% open-source under the MIT license. You can use it completely free forever.

### Q2: Do I have to pay for an AI API key?
**No!** Helper-AI comes with a built-in deterministic Smart Rule Engine and supports free local Ollama AI models. You can run it 100% offline without spending a penny.

### Q3: How does the new Reverse Engineering feature help me?
Whenever Helper-AI interacts with an application (like Notepad, Calculator, or Spotify), it understands the app's internal controls and hotkeys and saves them to memory. Next time you want to do something in that app, it executes in 1 second with 100% accuracy without wandering mouse clicks.

### Q4: When I double-click `start.bat`, nothing happens or it closes immediately. What should I do?
Make sure Python is installed and that you checked the box **"Add Python to PATH"** during installation. You can test this by opening PowerShell or Command Prompt and typing `python --version`.

### Q5: How do I stop an ongoing task?
Simply click the red **`⏹ Stop Agent`** button on the web dashboard at any time. Helper-AI will stop immediately.

### Q6: Can Helper-AI speak to me?
**Yes!** You can ask Helper-AI: `"Speak aloud: Welcome to my computer!"` and it will use its built-in neural text-to-speech engine to speak aloud in a natural human voice.

---

## 🧪 Automated Testing Suite

We maintain an exhaustive automated test suite with **175+ passing tests** covering every tool, network adapter, reverse engineering bridge, and browser controller:

```bash
# Run the complete test suite
pytest tests/ -v

# Run the reverse engineering integration tests
pytest tests/test_reverse_engineering_integration.py -v

# Run the security toolkit tests
pytest tests/test_security_toolkit.py -v
```

---

## 🤝 Community & Support

* **Detailed User Manual:** Read the [HOW_TO_USE.md](HOW_TO_USE.md) guide for in-depth examples in English and Gujarati.
* **Security Inquiries:** Review our [SECURITY.md](SECURITY.md) policy.
* **Contributing:** Read our [CONTRIBUTING.md](CONTRIBUTING.md) guide to help build new features.
* **Release History:** Check our [CHANGELOG.md](CHANGELOG.md) for all updates.

---

## 📄 License

Distributed under the open-source **[MIT License](LICENSE)**. Free to use, modify, and distribute.
