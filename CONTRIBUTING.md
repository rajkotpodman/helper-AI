# Contributing to Helper-AI

Thank you for your interest in contributing to **Helper-AI**! We welcome bug reports, feature suggestions, architecture proposals, and code contributions from developers of all skill levels.

This guide provides exhaustive guidelines for setting up your development environment, creating tools, running test suites, and submitting pull requests.

---

## 📋 Table of Contents
1. [Code of Conduct](#-code-of-conduct)
2. [Prerequisites & Development Setup](#-prerequisites--development-setup)
3. [Architecture Overview & Tool Development](#-architecture-overview--tool-development)
4. [Testing & Quality Verification](#-testing--quality-verification)
5. [Git Workflow & Commit Conventions](#-git-workflow--commit-conventions)
6. [Pull Request Checklist](#-pull-request-checklist)
7. [Reporting Bugs & Proposing Features](#-reporting-bugs--proposing-features)

---

## 🤝 Code of Conduct
All contributors and maintainers are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat all members of the community with respect, constructive feedback, and professional courtesy.

---

## 🛠️ Prerequisites & Development Setup

### 1. Requirements
- **Python:** 3.10, 3.11, or 3.12
- **Operating System:** Windows 10/11, Ubuntu 20.04+, or macOS 12+
- **Git:** 2.30+
- **Optional Tools:** Docker Desktop, Google Chrome (for Selenium / Playwright automation), Ollama (for offline LLM testing).

### 2. Fork and Clone
```bash
# 1. Fork the repository on GitHub, then clone your fork:
git clone https://github.com/<your-username>/helper-AI.git
cd helper-AI

# 2. Add upstream remote:
git remote add upstream https://github.com/rajkotpodman/helper-AI.git
```

### 3. Create Virtual Environment
```bash
# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
# Upgrade pip:
python -m pip install --upgrade pip

# Install all production & dev dependencies:
pip install -r requirements.txt
pip install -e ".[dev]"

# Install pre-commit hooks:
pre-commit install
```

---

## 🏛️ Architecture Overview & Tool Development

Helper-AI follows an extensible, modular architecture:

```text
helper-AI/
├── app.py                     # FastAPI application & WebSocket server
├── helper.py                  # Standalone CLI entrypoint
├── core/
│   ├── agent.py               # ReAct Planning & Execution Loop
│   ├── browser_driver.py      # Selenium & Chrome session manager
│   ├── voice_engine.py        # Edge-TTS speech synthesis engine
│   ├── playwright_agent.py    # Playwright DOM and visual analysis
│   ├── memory_recorder.py     # Markdown interaction logging & 20MB rotation
│   ├── permissions.py         # Human-in-the-Loop authorization manager
│   ├── llm.py                 # Multi-provider client (Gemini, OpenAI, Groq, Ollama)
│   ├── command_engine/        # Universal cross-platform terminal & cheatsheet engine
│   └── tools/                 # Native tool definitions (28 tools registered)
│       ├── system_tools.py    # PowerShell, process, health diagnostics
│       ├── file_tools.py      # Smart filesystem path resolver
│       ├── web_tools.py       # DuckDuckGo search & HTTP scraper
│       ├── browser_tools.py   # Social media & browser automation
│       ├── desktop_gui_tools.py # PyAutoGUI mouse, keyboard, window control
│       └── universal_terminal_tools.py # OS-adaptive execution, command hub
├── security_toolkit/          # Modular defensive security & FIM toolkit
└── tests/                     # 153+ automated unit & integration tests
```

### 🌟 Non-Technical Contributions (Everyone Can Help!)
You do **not** need to write code to contribute to Helper-AI! We warmly welcome:
1. **Testing Real-World Prompts:** Try out goals on your computer and share ideas for what works great or where the agent can improve.
2. **Improving Documentation:** Fix typos, add clearer explanations, or translate guides into more regional languages.
3. **Sharing Everyday Ideas:** Suggest practical automations for daily computer tasks, file organizing, or study workflows.
4. **Reporting Usability Roadblocks:** If something was confusing or hard to set up, let us know by opening an issue so we can make it even easier for everyone!

### How to Add a New Tool:
1. Define your tool function with clear type annotations and Google-style docstrings.
2. Register the tool in `core/tools/__init__.py` using the `@registry.register` decorator:
   ```python
   @registry.register(
       name="my_custom_tool",
       description="Detailed description for the LLM prompt of what the tool accomplishes.",
       parameters={
           "type": "object",
           "properties": {
               "param1": {"type": "string", "description": "Parameter details"}
           },
           "required": ["param1"]
       }
   )
   def my_custom_tool(param1: str) -> Dict[str, Any]:
       # Implementation logic
       return {"status": "success", "data": "result"}
   ```
3. Add a dedicated test in `tests/test_tools.py` verifying both success and edge error cases.

---

## 🧪 Testing & Quality Verification

All contributions must pass the complete automated test suite before merging:

```bash
# Run entire test suite:
pytest -v

# Run with coverage report:
pytest --cov=core tests/

# Run code style & formatting checks:
black --check .
flake8 core/ tests/
```

On Linux or CI environments without a physical display, run tests under virtual framebuffer:
```bash
xvfb-run --auto-servernum pytest tests/ -v
```

---

## 🌿 Git Workflow & Commit Conventions

We strictly enforce **Conventional Commits**:

| Type | Description | Example |
| :--- | :--- | :--- |
| `feat` | New feature or capability | `feat(browser): add multi-tab switching action` |
| `fix` | Bug fix or error resolution | `fix(facebook): resolve button click intercepted by modal` |
| `docs` | Documentation update | `docs(gujarati): expand voice synthesis setup guide` |
| `test` | Adding or updating tests | `test(agent): add test for auto-retry backoff` |
| `refactor`| Code refactoring without behavioral change | `refactor(llm): optimize token stream normalization` |
| `ci` | CI/CD or workflow adjustments | `ci(actions): update docker buildx action repository` |

### Step-by-Step Branching:
```bash
# 1. Sync local main with upstream:
git checkout main
git pull upstream main

# 2. Create feature branch:
git checkout -b feat/your-feature-name

# 3. Make changes, run tests, and commit:
git add .
git commit -m "feat(scope): concise description of changes"

# 4. Push to your fork:
git push -u origin feat/your-feature-name
```

---

## 📋 Pull Request Checklist
Before opening a PR, ensure:
- [ ] Code follows project formatting (Black, Flake8).
- [ ] All unit and integration tests pass cleanly (`pytest -v`).
- [ ] New features include corresponding test coverage.
- [ ] Relevant documentation (`README.md`, `HOW_TO_USE.md`) has been updated.
- [ ] Commit history is clean and uses Conventional Commit titles.

Thank you for helping make **Helper-AI** the most capable autonomous desktop and web agent!
