<div align="center">

# ⚡ Helper-AI
### Autonomous AI Agent with Full PC & Internet Control

*Give Helper a goal. It executes, self-heals, and works until the job is done—without endless questioning.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

</div>

---

## 🌟 What is Helper-AI?

**Helper-AI** is an autonomous personal AI agent designed to bridge the gap between high-level human goals and real operating system actions. Unlike basic chatbots that only answer questions with text, **Helper-AI takes direct action on your PC and the internet**.

Whether you need to clean up messy folders, diagnose system performance, research an internet topic and save a summary report to your Desktop, or run complex PowerShell tasks—**Helper plans the steps, runs the tools, inspects the results, fixes errors on the fly, and stops only when your goal is accomplished.**

---

## 🎯 Key Capabilities

### 💻 1. Full Running PC Control
- **PowerShell & Terminal Automation:** Executes PowerShell/CMD commands, tests tools, installs software, and manages services.
- **Smart File System Operations:** Reads, writes, moves, searches, and organizes files. Recognizes shortcuts like `Desktop`, `Downloads`, and `Documents` automatically.
- **Process & Health Monitoring:** Real-time CPU, RAM, and Disk inspection with the ability to locate and terminate frozen processes.
- **App & Document Launching:** Opens desktop apps, URLs, folders, or documents seamlessly.

### 🌐 2. Internet & Web Automation
- **Built-in Web Search:** Searches DuckDuckGo for live internet answers and documentation without requiring any paid search API keys.
- **Web Content Extraction:** Fetches and parses articles, documentation, or websites into clean, ad-free text.
- **Direct File Downloads:** Streams and downloads files directly from the web into designated folders.

### 🚀 3. Autonomous "No-Questions" Execution
- **Autonomous ReAct Engine:** Plans → Acts → Observes → Self-Corrects.
- **Error Recovery:** If a command fails or a file isn't found, Helper analyzes the error and formulates an alternative approach instead of giving up.
- **Non-Technical Friendly:** Features both a **1-click Web Dashboard** and a powerful CLI. Anyone can use it without prior coding knowledge.

---

## 🚀 Quick Start (Non-Technical Users)

### Option A: The 1-Click Starter (Windows)
1. Download or clone this repository to your computer.
2. Double-click **`start.bat`**.
3. Your browser will automatically launch with the **Helper-AI Web Dashboard** (`http://localhost:8000`).
4. Type your goal and click **Execute Goal**!

---

## 🛠️ Quick Start (Developers & Power Users)

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/rajkotpodman/helper-AI.git
cd helper-AI
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Set your preferred provider:
```ini
LLM_PROVIDER=gemini       # Options: gemini, openai, groq, ollama, rule_engine
GEMINI_API_KEY=your_key_here
```
*(Note: Helper-AI works even without an API key using the built-in Smart Rule Engine for standard PC and web tasks!)*

### 3. Launch the Web Dashboard
```bash
python app.py
```
Visit `http://localhost:8000` in your browser.

### 4. Or Run Directly from Terminal (CLI Mode)
```bash
# Direct goal execution
python helper.py "Check my PC health, CPU, and RAM, and write a summary to Desktop/health.txt"

# Search web and save report
python helper.py "Search the web for top open-source AI agents and save a report to Desktop/report.md"

# Interactive prompt
python helper.py
```

---

## 🧩 Supported AI Models

| Provider | Model | Description |
| :--- | :--- | :--- |
| **Google Gemini** | `gemini-1.5-flash` | *(Recommended)* Blazing fast, huge context window, inexpensive or free tier. |
| **OpenAI** | `gpt-4o` / `gpt-4o-mini` | State of the art reasoning and planning. |
| **Groq** | `llama-3.3-70b-versatile` | Ultra-low latency execution. |
| **Ollama** | `llama3.2` / `mistral` | **100% Offline & Private.** Runs locally on your machine with zero data leaving your PC. |
| **Rule Engine** | *Built-in* | Zero setup fallback for standard PC diagnostics, file management, and web searches. |

---

## 📁 Project Structure

```text
helper-AI/
├── app.py                  # Web Dashboard server (FastAPI + WebSocket)
├── helper.py               # CLI runner for power users
├── start.bat               # 1-click Windows launcher
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment settings template
├── LICENSE                 # MIT License
├── core/
│   ├── agent.py            # Autonomous ReAct agent loop
│   ├── llm.py              # Multi-provider LLM interface (Gemini/OpenAI/Groq/Ollama)
│   ├── memory.py           # Context and execution trajectory manager
│   └── tools/              # PC and Internet tool implementations
│       ├── base.py         # Base tool schema & abstract class
│       ├── system_tools.py # PowerShell runner, system health, process manager
│       ├── file_tools.py   # Smart file reader, writer, search, and organizer
│       └── web_tools.py    # DuckDuckGo search, web scraper, downloader
└── static/
    ├── css/style.css       # Modern dark-mode glassmorphism interface
    ├── js/app.js           # Live WebSocket and agent controller
    └── index.html          # Web dashboard interface
```

---

## 🛡️ Safety & Autonomous Guardrails

Helper-AI provides two operating modes:
- **Full Autonomous Mode (Default):** Runs commands and solves problems without interrupting you with questions.
- **Safe Mode:** Can be toggled on in Settings or with `--safe` in CLI. It restricts potentially destructive PowerShell commands (such as recursive drive format or deletion).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
