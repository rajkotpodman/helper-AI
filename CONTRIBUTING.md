# Contributing to Helper-AI

Thank you for your interest in contributing to **Helper-AI**! We welcome bug reports, feature suggestions, architecture proposals, and code contributions.

---

## 🛠️ Development Setup

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Local Setup
```bash
# Clone your fork
git clone https://github.com/rajkotpodman/helper-AI.git
cd helper-AI

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### 3. Running Tests
We maintain 100% test pass rate for all tools and core engines:
```bash
pytest tests/ -v
```

---

## 🌿 Branching Strategy & Pull Requests

1. **Fork & Branch:** Create a feature branch off `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Commit Guidelines:** Use [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: add new internet scraping tool`
   - `fix: resolve windows path resolution for nested directories`
   - `docs: improve gujarati usage guide`
   - `test: add unit tests for audit logging`
3. **Verify:** Ensure all unit tests pass before opening a PR:
   ```bash
   pytest
   ```
4. **Submit PR:** Open a Pull Request against `main` with a clear description and screenshots/terminal recordings if applicable.

---

## 🛡️ Security Vulnerabilities
Please do **NOT** open public issues for security vulnerabilities. Review our [SECURITY.md](SECURITY.md) for responsible disclosure.
