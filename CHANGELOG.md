# Changelog

All notable changes to the **Helper-AI** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.5.0] - 2026-10-13

### 🛡️ Universal Cross-Platform Terminal & Security Toolkit Architecture
- **Universal Cross-Platform Terminal Engine (`core/command_engine/`):**
  - Added OS and shell auto-detection (`os_detector.py`) supporting Windows (PowerShell/CMD), Linux (POSIX Bash/Zsh), macOS, WSL, and BSD.
  - Implemented encyclopedic command catalog and recipe synthesizer (`command_encyclopedia.py`) mapping natural language goals to native terminal commands.
  - Added dynamic community command cheat sheet downloader and persistent local cache (`command_fetcher.py`).
  - Added universal executor (`executor.py`) supporting synchronous execution and heavy background daemons with log capture, status querying, and cancellation.
  - Registered 3 new native tools: `universal_terminal`, `synthesize_os_command`, and `command_hub`, expanding the arsenal to 28 tools.
- **Defensive Security & Vulnerability Assessment Toolkit (`security_toolkit/`):**
  - Non-blocking asynchronous network port scanner (`port_scanner.py`) with semaphore concurrency and service identification.
  - OWASP HTTP security header analyzer (`header_analyzer.py`) evaluating defensive posture, technology disclosure penalties, and letter grades (A+ to F).
  - Cryptographic SHA-256 File Integrity Monitoring engine (`integrity_checker.py`) for drift, tamper, and unauthorized drop detection.
  - Multi-format exporter (`reporter.py`) generating JSON, CSV findings, and platform-safe ASCII reports.
  - Unified CLI command router (`cli.py`).
- **Non-Technical User Experience & Documentation:**
  - Expanded `README.md` and `HOW_TO_USE.md` with beginner-friendly guides, ASCII dashboard schematics, and bilingual (English & Gujarati) walkthroughs.
  - Test suite expanded to 153+ passing automated tests with 100% pass rate.

---

## [1.4.0] - 2026-10-12

### 🚀 Autonomous Self-Healing & DevOps CI/CD Overhaul
- **Self-Healing Execution Loop Architecture:**
  - Implemented multi-strategy execution queues (Strategy A: Direct Selector Click; Strategy B: Synthetic JavaScript Event Trigger; Strategy C: Keyboard Tab/Enter Traversal; Strategy D: Coordinates & Bounding Box Click).
  - Integrated adaptive retry controller with exponential backoff and error signature classification.
  - Added autonomous post-execution verification inspecting DOM readiness, URL mutations, and filesystem downloads.
- **Universal Translation & Gujarati Synthesis Hub:**
  - Integrated `deep-translator` backend supporting all 130+ Google Translate language codes.
  - Automatic input language detection with regex-based Unicode script identification.
  - Detailed 5-section technical report synthesis in native **Gujarati (ગુજરાતી)** covering task objective, web research, executed actions, retry handling, and verified data.
- **Continuous Integration & Automation Hardening:**
  - Repaired GitHub Actions workflow configurations across Linux and Windows matrices (`ci.yml`, `docker-build.yml`, `codeql.yml`, `release.yml`).
  - Added headless Xvfb virtual framebuffer support for Ubuntu runners to ensure 100% headless PyAutoGUI / Selenium stability.
  - Standardized Docker multi-stage build (`Dockerfile`) with build toolchains and healthcheck verification endpoints.
  - Complete dependency synchronization across `requirements.txt` and `pyproject.toml` including `selenium`, `webdriver-manager`, `pyautogui`, `edge-tts`, and `playwright`.

---

## [1.3.0] - 2026-10-11

### 🌐 Social Media Automation & LLM Failover Resilience
- **Facebook & Social Publishing Pipeline:**
  - Resolved Facebook post submission stalls using exact button targeting, Ctrl+Enter keyboard fallback, and automated modal dismissals.
  - Added support for draft social post creation and publication across X/Twitter, LinkedIn, Facebook, Threads, and Reddit.
  - Integrated persistent browser user profile maintaining authentication sessions across agent invocations.
- **Multi-Model LLM Resilience:**
  - Integrated official Google Gemini API client (`google-genai`) with automatic failover fallback between Gemini, OpenAI, Groq, Ollama, and the local deterministic Rule Engine.
  - Added LLM response JSON normalization handling mixed code fences, markdown wrapping, and malformed completions.

---

## [1.2.0] - 2026-10-10

### 🎙️ 4 Open-Source Phases Integration
- **Voice Synthesis Engine (`core/voice_engine.py`):**
  - Integrated `edge-tts` for high-fidelity zero-cost neural text-to-speech supporting multiple global accents and natural inflections.
- **Playwright Vision Engine (`core/vision_browser.py`):**
  - Added high-resolution viewport capture, visual DOM state inspection, and multimodal layout comprehension.
- **Model Context Protocol (MCP) Manager (`core/tools/mcp_client.py`):**
  - Standardized external tool integration adhering to Anthropic's Model Context Protocol specification (`mcp_servers.json`).
  - Dynamically registers third-party tools into the agent's runtime tool registry.
- **Desktop GUI Control Arsenal (`core/tools/desktop_gui_tools.py`):**
  - Added mouse simulation (click, double click, drag, scroll), keyboard shortcuts, active window management, and clipboard synchronization via PyAutoGUI.

---

## [1.1.0] - 2026-10-09

### 📝 Blogger & Web Platform Automation
- **Project Browser Integration (`core/browser_driver.py`):**
  - Dedicated Selenium Chrome driver with anti-detection evasions (`--disable-blink-features=AutomationControlled`).
  - Automated blog post drafting, HTML rendering, label assignment, and publishing confirmation for Blogger / Blogspot.
- **Challenge Detection & Human-in-the-Loop (HITL):**
  - Autonomous heuristic detection for Cloudflare Turnstile, reCAPTCHA, and 2FA authentication screens.
  - Non-blocking permission manager triggering approval modals on the web dashboard.

---

## [1.0.0] - 2026-10-07

### ⚡ Initial Release: Zero-Cloud Autonomous Edge Agent
- **Core Autonomous ReAct Loop:** Plan-Act-Observe-Self-Heal architecture.
- **Full PC Control Arsenal:** PowerShell execution, Process manager, System Health diagnostics, and App launcher.
- **Smart File System Operations:** Auto-resolves user paths (`Desktop`, `Downloads`, `Documents`).
- **Web & Internet Automation:** DuckDuckGo live search, webpage reader, and direct downloader without paid API keys.
- **Multi-Provider LLM Engine:** Google Gemini, OpenAI (GPT-4o), Groq, Ollama (100% offline), and built-in Smart Rule Engine.
- **Modern Glassmorphic Web Dashboard:** FastAPI + WebSocket real-time step streaming.
- **Enterprise Observability:** Structured JSONL audit logging (`audit.log`) with secret masking and telemetry metrics (`/api/metrics`).
- **Developer Experience:** 1-click Windows starter (`start.bat`), CLI runner (`helper.py`), and PEP 518/621 `pyproject.toml`.
- **Quality & DevOps:** 100% passing pytest automated test suite and multi-OS GitHub Actions CI/CD pipeline.
- **Documentation:** Full English README and in-depth Gujarati user guide (`HOW_TO_USE.md`).
