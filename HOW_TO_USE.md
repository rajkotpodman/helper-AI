# ⚡ Helper-AI: Complete Non-Technical Master User Manual
### (સંપૂર્ણ માર્ગદર્શિકા - English & ગુજરાતી Bilingual Edition)

> **Welcome to Helper-AI!** This guide is written specifically for **non-technical users, everyday computer owners, students, and professionals**. You do **not** need to be a programmer or know any coding to use Helper-AI.

---

## 📑 Table of Contents / અનુક્રમણિકા

### 🌐 Part 1: English Master Manual for Non-Technical Users
1. [What is Helper-AI and How Does It Work?](#1-what-is-helper-ai)
2. [1-Click Setup Guide (Windows, Mac, Linux)](#2-1-click-setup-guide)
3. [Understanding the Web Dashboard Screen](#3-understanding-the-web-dashboard-screen)
4. [How to Give Goals to the Agent (Best Prompting Practices)](#4-how-to-give-goals-to-the-agent)
5. [The Complete 28-Tool Arsenal Explained in Plain English](#5-the-complete-28-tool-arsenal-explained)
6. [Everyday Practical Recipes & Real-World Examples](#6-everyday-practical-recipes)
   - [A. Cleaning & Organizing Messy Computer Folders](#a-cleaning--organizing-messy-computer-folders)
   - [B. Researching the Internet & Generating Document Reports](#b-researching-the-internet--generating-document-reports)
   - [C. Computer Speed, Health & Killing Frozen Programs](#c-computer-speed-health--killing-frozen-programs)
   - [D. Browser Automation & Social Media Publishing](#d-browser-automation--social-media-publishing)
   - [E. Running Any Terminal or PowerShell Command Safely](#e-running-any-terminal-or-powershell-command-safely)
   - [F. Defensive Security Audits & File Protection](#f-defensive-security-audits--file-protection)
   - [G. Voice Speech (Hearing the Agent Speak Aloud)](#g-voice-speech-hearing-the-agent-speak-aloud)
7. [Running 100% Free & Offline (No Paid Keys Needed)](#7-running-100-free--offline)
8. [Safe Mode & 1-Click Approval Dialogs](#8-safe-mode--1-click-approval-dialogs)
9. [Beginner Troubleshooting & FAQ](#9-beginner-troubleshooting--faq)

---

### 🇮🇳 Part 2: ગુજરાતી વિભાગ (Gujarati Section)
1. [Helper-AI શું છે અને તે કેવી રીતે કામ કરે છે?](#૧-helper-ai-શું-છે)
2. [૧-ક્લિકમાં ચાલુ કરવાની રીત](#૨-૧-ક્લિકમાં-ચાલુ-કરવાની-રીત)
3. [વેબ ડેશબોર્ડનો સરળ ઉપયોગ](#૩-વેબ-ડેશબોર્ડનો-સરળ-ઉપયોગ)
4. [૨૮ પાવરફુલ ટૂલ્સની યાદી અને વાસ્તવિક ઉદાહરણો](#૪-૨૮-પાવરફુલ-ટૂલ્સની-યાદી)
5. [રોજિંદા જીવનમાં ઉપયોગી પ્રોમ્પ્ટ્સ (Ready-Made Goals)](#૫-રોજિંદા-જીવનમાં-ઉપયોગી-પ્રોમ્પ્ટ્સ)
6. [API Key વગર ૧૦૦% ફ્રી અને ઑફલાઇન ચલાવવાની રીત](#૬-api-key-વગર-૧૦૦-ફ્રી-અને-ઑફલાઇન)
7. [સુરક્ષા અને ૧-ક્લિક મંજૂરી (Human-in-the-Loop)](#૭-સુરક્ષા-અને-૧-ક્લિક-મંજૂરી)
8. [વારંવાર પૂછાતા પ્રશ્નો (FAQ)](#૮-વારંવાર-પૂછાતા-પ્રશ્નો-faq)

---

# 🌐 PART 1: ENGLISH MASTER MANUAL

---

## 1. What is Helper-AI?

Normal chatbots (like standard ChatGPT or Claude) can only chat with you. If you ask them to clean up your computer, they can give you advice, but they **cannot** actually touch your files, click buttons, or fix your computer.

**Helper-AI is completely different.** It is an **Autonomous Computer Agent**:
- It has safe, direct access to your computer and the internet.
- When you tell it: *"Check my Downloads folder and group files by extension"*, Helper-AI **actually looks at your folder, creates subfolders, moves the files, verifies they are moved, and tells you when it is done.**
- If an unexpected error happens (like a locked file or a missing folder), it doesn't give up! It reads the error message, adjusts its plan, and tries another method until the task is finished.
- It doesn't bother you with 20 questions—it works toward the goal autonomously.

---

## 2. 1-Click Setup Guide

You only need **Python** installed on your computer.

### Step 1: Install Python (If you don't have it)
1. Go to **[https://www.python.org/downloads/](https://www.python.org/downloads/)**.
2. Download the installer.
3. ⚠️ **IMPORTANT CHECKBOX:** On the very first screen of the installer, check the box:
   **☑ Add python.exe to PATH**
4. Click **Install Now**.

### Step 2: Download Helper-AI
1. Click the green **Code** button at the top of the repository and choose **Download ZIP**.
2. Extract the ZIP folder anywhere on your computer (e.g. `C:\helper-ai` or your `Desktop`).

### Step 3: Run Helper-AI
- **On Windows:** Double-click the file named **`start.bat`**.
- **On Mac or Linux:** Open a terminal in the folder and type:
  ```bash
  python app.py
  ```
That's it! Your web browser will automatically open up at:
👉 **`http://localhost:8000`**

---

## 3. Understanding the Web Dashboard Screen

When you open `http://localhost:8000`, you will see a clean, dark-themed control center:

```text
+-----------------------------------------------------------------------------------------+
| ⚡ Helper-AI                     [● System Ready]      [⚙️ Settings]      [🛡️ Safe Mode]  |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|   🎯 What goal would you like Helper to achieve?                                        |
|   +---------------------------------------------------------------------------------+   |
|   | [ Type your goal here in plain human language...                              ] |   |
|   +---------------------------------------------------------------------------------+   |
|                                                                                         |
|   Quick Action Buttons:                                                                 |
|   [💻 Check PC Health]  [🔍 Research Web & Save Report]  [📂 Inspect Downloads]         |
|   [🛡️ Audit Open Ports]  [🌐 List GitHub Repositories]   [📝 Create Social Media Post]  |
|                                                                                         |
|   Safe Mode: Off (Full Autonomous)                       [⏹ Stop Agent] [🚀 Execute Goal]|
+-----------------------------------------------------------------------------------------+
| 📊 Real-Time Execution Feed                                                             |
|   Step 1: 💭 Thought: "I need to check the Downloads directory and group files by type."|
|           ⚡ Action: list_directory(path="Downloads")                                   |
|           📋 Result: Found 24 files (10 images, 8 PDFs, 6 installers)                   |
|   Step 2: 💭 Thought: "Creating subfolders and moving files..."                         |
|   ...                                                                                   |
|   🎉 MISSION ACCOMPLISHED! Your files have been organized into neat subfolders.         |
+-----------------------------------------------------------------------------------------+
```

### Key Elements of the Screen:
1. **The Goal Box:** Type your instructions here in plain, natural language.
2. **Quick Action Buttons:** One-click shortcuts for popular everyday tasks.
3. **`🚀 Execute Goal` Button:** Starts the autonomous agent.
4. **`⏹ Stop Agent` Button:** Immediately pauses or cancels whatever the agent is doing.
5. **Real-Time Execution Feed:** Shows you exactly what the agent is thinking, what tools it is running, and what output your computer is returning.

---

## 4. How to Give Goals to the Agent

You do not need to speak "code." Just talk to Helper-AI like a helpful colleague.

### 🌟 Good vs. Vague Prompts:
- **Instead of:** *"Files"*  
  **Say:** *"Look at my Downloads folder, find all PDF files, and list them on my screen."*
- **Instead of:** *"Is my PC slow?"*  
  **Say:** *"Check my PC health, tell me how much RAM is being used, and save a report to Desktop/pc_health.txt."*
- **Instead of:** *"AI news"*  
  **Say:** *"Search the internet for the top 3 AI news stories this week and save a summary to Desktop/ai_news.md."*

---

## 5. The Complete 28-Tool Arsenal Explained

Here is what every tool does in simple words:

1. **`universal_terminal`**: Runs any command on your computer (PowerShell, Windows CMD, Linux Bash, Mac Zsh) and can run heavy background tasks without freezing your screen.
2. **`synthesize_os_command`**: Turns your simple request (like *"kill the app using port 8000"*) into the exact command needed for your specific computer.
3. **`command_hub`**: Downloads and displays cheat sheets and instructions for any tool (like `ffmpeg`, `docker`, `powershell`, or `curl`).
4. **`audit_security_baseline`**: Scans your computer for defensive security: checks firewall status, open network ports, and missing security updates.
5. **`deep_web_crawl`**: Explores entire websites, documentation portals, or blogs, saving the text into one clean document for you.
6. **`batch_fetch_web`**: Downloads and extracts multiple web pages simultaneously.
7. **`fetch_github_repo`**: Downloads code, README files, and repository lists from GitHub without needing Git installed.
8. **`fetch_web_content`**: Reads any article or webpage on the internet, stripping away ads and popups.
9. **`duckduckgo_search`**: Searches the live internet for free without needing any paid search subscription.
10. **`download_file`**: Downloads files, PDFs, or software directly to your computer.
11. **`execute_python_code`**: Runs Python code safely and automatically installs any missing packages.
12. **`build_project_files`**: Creates full multi-file projects, websites, or folders in a single click.
13. **`execute_powershell`**: Runs native Windows commands with automatic fixing for folder paths with spaces.
14. **`read_file`**: Opens and reads any text or document file on your hard drive.
15. **`write_file`**: Creates a new file or saves information to a text file.
16. **`list_directory`**: Shows you all files and subfolders inside any folder (like your Desktop or Downloads).
17. **`search_files`**: Finds files across your computer by name or file type (e.g. `*.docx` or `*.jpg`).
18. **`move_or_copy_file`**: Moves, copies, or renames files safely.
19. **`process_manager`**: Shows you which programs are running and closes frozen apps.
20. **`system_health`**: Shows CPU usage, RAM memory, and hard drive free space.
21. **`open_application`**: Opens apps on your computer like Chrome, Notepad, Calculator, or Spotify.
22. **`manage_ollama`**: Lets you download and run 100% private, free AI models on your own PC.
23. **`check_connections`**: Tests whether your internet, Google Translate, and local servers are connected.
24. **`browser_automation`**: Controls a web browser to log in, fill out forms, or post to social media.
25. **`desktop_gui_control`**: Moves your mouse cursor, clicks buttons on your screen, and presses keyboard shortcuts (`Ctrl+C`, `Ctrl+V`).
26. **`text_to_speech`**: Speaks out loud in a natural human voice using Microsoft's neural voice engine.
27. **`vision_browser`**: Takes visual screenshots of websites and inspects the screen layout.
28. **`mcp_tool`**: Connects external third-party tools via the Model Context Protocol.

---

## 6. Everyday Practical Recipes

### A. Cleaning & Organizing Messy Computer Folders
**Goal to type:**
> *"Look at my Downloads folder, create separate folders for Images, Documents, and Installers, and move the matching files into their respective folders."*

**What happens:**
1. Helper-AI scans `Downloads`.
2. It detects `.png` / `.jpg` as images, `.pdf` / `.docx` as documents, and `.exe` as installers.
3. It creates the new folders and moves the files cleanly.

---

### B. Researching the Internet & Generating Document Reports
**Goal to type:**
> *"Search the web for the top 5 electric vehicles coming in 2026. Write a comprehensive report with bullet points and save it to Desktop/ev_report.md."*

**What happens:**
1. Helper-AI searches DuckDuckGo for the newest news.
2. It reads the top articles.
3. It formats a professional markdown document and saves it directly to your Desktop.

---

### C. Computer Speed, Health & Killing Frozen Programs
**Goal to type:**
> *"Check which programs are using the most memory on my PC. If any program is using more than 2 GB of RAM, tell me."*

Or to free up a stuck port:
> *"Find whatever process is holding port 8000 and close it."*

---

### D. Browser Automation & Social Media Publishing
**Goal to type:**
> *"Open LinkedIn and create a post summarizing why autonomous AI agents save time for small businesses. Publish it to my feed."*

Helper-AI opens its dedicated project browser, navigates to your feed, types the text, and publishes the update cleanly.

---

### E. Running Any Terminal or PowerShell Command Safely
**Goal to type:**
> *"Run a terminal command to find all files larger than 500 MB on my C: drive."*

Helper-AI automatically detects if you are on Windows, Mac, or Linux, creates the correct command syntax, runs it, and gives you a neat table of files.

---

### F. Defensive Security Audits & File Protection
**Goal to type:**
> *"Run a defensive security audit on my computer to check which network ports are currently listening for connections."*

Helper-AI will list all open ports (e.g. 80, 443, 8000) and tell you what program owns each port.

---

### G. Voice Speech (Hearing the Agent Speak Aloud)
**Goal to type:**
> *"Speak aloud: Good morning! Your computer is running smoothly and all backups are complete."*

Helper-AI will generate neural audio and play it directly through your computer speakers.

---

## 7. Running 100% Free & Offline

You do **not** need to buy or subscribe to any paid service:
1. **Default Mode (Rule Engine):** Helper-AI includes a deterministic Rule Engine that knows how to route everyday computer commands immediately without any API keys.
2. **Local AI via Ollama:** You can install [Ollama](https://ollama.com/) (completely free) and download a model like `qwen2.5:1.5b`. Helper-AI will connect to it locally and think 100% privately on your computer.
3. **Free Google Gemini Key (Optional):** If you want frontier cloud AI, visit [Google AI Studio](https://aistudio.google.com/), click "Create API Key", and paste it into `.env` under `GEMINI_API_KEY=`. Google provides free daily requests.

---

## 8. Safe Mode & 1-Click Approval Dialogs

When you turn on **Safe Mode** in the dashboard:
- Any action that could modify your system, delete a file, or post to social media will **pause** execution.
- A friendly popup will appear on your screen:
  ```text
  🛡️ Action Requires Your Approval:
  Helper-AI wants to publish a post on LinkedIn:
  "Here is my post text..."
  
  [✅ Approve Action]       [❌ Reject Action]
  ```
- Nothing happens without your explicit consent!

---

## 9. Beginner Troubleshooting & FAQ

### Q1: I clicked `start.bat`, but a black window flashed and closed.
**Solution:** Python is not added to your system's PATH. Reinstall Python from `python.org` and make sure to check the box **"Add python.exe to PATH"** on the first install screen.

### Q2: It says "Port 8000 already in use".
**Solution:** Another program (or a previous Helper-AI instance) is already using port 8000. Open Task Manager and close any existing `python.exe` processes, or run:
```powershell
Stop-Process -Name python -Force
```
Then double-click `start.bat` again.

### Q3: Can I run Helper-AI in Gujarati, Hindi, or other languages?
**Yes!** Helper-AI understands multiple languages. You can type your goals in Gujarati, Hindi, Spanish, or English, and Helper-AI will understand your intent and execute the task.

---
---

# 🇮🇳 PART 2: ગુજરાતી વિભાગ (GUJARATI SECTION)

---

## ૧. Helper-AI શું છે?

સામાન્ય ચેટબોટ્સ (જેવા કે સામાન્ય ChatGPT) ફક્ત તમને લખાણમાં જવાબો આપે છે, પરંતુ તે તમારા કમ્પ્યુટર પર જાતે કોઈ કામ કરી શકતા નથી. 

**Helper-AI અલગ છે:**
* તે એક **ઓટોનોમસ એજન્ટ (Autonomous Agent)** છે.
* તે તમારા કમ્પ્યુટર અને ઈન્ટરનેટનું **સંપૂર્ણ નિયંત્રણ (Full Control)** ધરાવે છે.
* તમે તેને ફક્ત એક લક્ષ્ય (Goal) આપો, તે જાતે પ્લાન બનાવશે, કમાન્ડ ચલાવશે, ફાઈલો તપાસશે, ઈન્ટરનેટ પર સર્ચ કરશે અને **તમને વારંવાર ડિસ્ટર્બ કર્યા વગર કામ પૂરું કરશે**.
* જો કોઈ પગલું ફેલ થાય, તો તે જાતે સુધારો કરી (Self-Healing) બીજી વ્યૂહરચના વાપરે છે.

---

## ૨. ૧-ક્લિકમાં ચાલુ કરવાની રીત

તમારે કોઈ કોડિંગ કે કમાન્ડ્સ ટાઈપ કરવાની જરૂર નથી:

1. ફોલ્ડર ખોલો: જ્યાં તમે પ્રોજેક્ટ સેવ કર્યો હોય (દા.ત. `E:\ai agent\`).
2. **`start.bat`** ફાઈલ પર **ડબલ-ક્લિક (Double Click)** કરો.
3. એક કાળી વિન્ડો ખૂલશે જે જરૂરી બધું આપમેળે ચેક કરશે.
4. થોડી જ સેકન્ડોમાં તમારા ડિફોલ્ટ બ્રાઉઝરમાં વેબસાઇટ ઓટોમેટિક ખૂલી જશે:  
   👉 **`http://localhost:8000`**

---

## ૩. વેબ ડેશબોર્ડનો સરળ ઉપયોગ

1. **ટેક્સ્ટ બોક્સમાં તમારું લક્ષ્ય લખો** (અથવા નીચે આપેલા તૈયાર બટનોમાંથી એક પસંદ કરો).
2. **`🚀 Execute Goal`** બટન પર ક્લિક કરો.
3. નીચે લાઈવ સ્ટેપ કાર્ડ્સ દેખાશે:
   - **💭 Thought (વિચાર):** એજન્ટ વિચારે છે કે હવે શું કરવું.
   - **⚡ Action (એક્શન):** કયો કમાન્ડ કે ટૂલ વપરાયું.
   - **📋 Terminal Output:** કમ્પ્યુટરમાંથી શું પરિણામ આવ્યું.
4. જ્યારે કામ પૂરું થાય ત્યારે લીલા રંગનું **🎉 MISSION ACCOMPLISHED!** બોક્સ આવી જશે.
5. જો વચ્ચે કામ અટકાવવું હોય, તો **`⏹ Stop Agent`** બટન દબાવો.

---

## ૪. ૨૮ પાવરફુલ ટૂલ્સની યાદી

1. **`universal_terminal`**: વિન્ડોઝ, લિનક્સ કે મેક પર કોઈપણ કમાન્ડ અથવા બેકગ્રાઉન્ડ પ્રોસેસ ચલાવે છે.
2. **`synthesize_os_command`**: તમારા સાદા લખાણને તમારી ઓપરેટિંગ સિસ્ટમ માટે યોગ્ય કમાન્ડમાં ફેરવે છે.
3. **`command_hub`**: કોઈપણ ટૂલ (જેમ કે ffmpeg, docker, powershell) માટે ઉપયોગી ચીટ-શીટ્સ ડાઉનલોડ કરે છે.
4. **`audit_security_baseline`**: કમ્પ્યુટરનું ફાયરવોલ, ઓપન પોર્ટ્સ અને સિક્યોરિટી ચેક કરે છે.
5. **`deep_web_crawl`**: આખી વેબસાઇટ કે ડોક્યુમેન્ટ પોર્ટલ વાંચીને ફાઇલ બનાવે છે.
6. **`batch_fetch_web`**: એકસાથે ઘણી બધી વેબસાઇટ્સમાંથી ડેટા લાવે છે.
7. **`fetch_github_repo`**: ગિટહબ પરથી કોડ, ફાઈલો અને રિલીઝ લિસ્ટ ડાઉનલોડ કરે છે.
8. **`fetch_web_content`**: કોઈપણ વેબસાઇટ પરથી જાહેરાત વગર ચોખ્ખી માહિતી વાંચે છે.
9. **`duckduckgo_search`**: ઈન્ટરનેટ પર તદ્દન ફ્રીમાં લાઈવ સર્ચ કરે છે.
10. **`download_file`**: ઈન્ટરનેટ પરથી સીધી ફાઈલ ડાઉનલોડ કરે છે.
11. **`execute_python_code`**: પાયથોન કોડ રન કરે છે અને ખૂટતા પેકેજો જાતે ઇન્સ્ટોલ કરે છે.
12. **`build_project_files`**: આખો સોફ્ટવેર પ્રોજેક્ટ કે ફોલ્ડર ૧ જ ક્લિકમાં બનાવે છે.
13. **`execute_powershell`**: વિન્ડોઝ પાવરશેલ કમાન્ડ્સ ચલાવે છે.
14. **`read_file`**: કમ્પ્યુટરની કોઈપણ ફાઈલ વાંચે છે.
15. **`write_file`**: નવી ફાઈલ બનાવે છે કે ફાઈલમાં લખે છે.
16. **`list_directory`**: ફોલ્ડરની અંદર કઈ ફાઈલો છે તે તપાસે છે.
17. **`search_files`**: આખા કમ્પ્યુટરમાંથી ફાઈલ શોધી આપે છે.
18. **`move_or_copy_file`**: ફાઈલોને એક જગ્યાએથી બીજી જગ્યાએ ખસેડે છે.
19. **`process_manager`**: ચાલુ પ્રોગ્રામ્સ તપાસે છે અને હેંગ થયેલી એપ બંધ કરે છે.
20. **`system_health`**: સીપીયુ, રેમ (મેમરી) અને હાર્ડ ડ્રાઈવની સ્પેસ બતાવે છે.
21. **`open_application`**: નોટપેડ, ક્રોમ, કેલ્ક્યુલેટર જેવી એપ્સ ખોલે છે.
22. **`manage_ollama`**: ૧૦૦% ઑફલાઇન ફ્રી AI મોડેલ ચલાવે છે.
23. **`check_connections`**: ઈન્ટરનેટ અને સર્વર કનેક્શન તપાસે છે.
24. **`browser_automation`**: સોશિયલ મીડિયા પર પોસ્ટ લખવા કે બટન દબાવવા બ્રાઉઝર કંટ્રોલ કરે છે.
25. **`desktop_gui_control`**: કમ્પ્યુટર સ્ક્રીન પર માઉસ ક્લિક અને કીબોર્ડ શોર્ટકટ ચલાવે છે.
26. **`text_to_speech`**: કુદરતી માનવ અવાજમાં લખાણ બોલીને સંભળાવે છે.
27. **`vision_browser`**: સ્ક્રીનશોટ પાડે છે અને વેબસાઇટનું લેઆઉટ જુએ છે.
28. **`mcp_tool`**: બહારના ત્રીજા પક્ષના ટૂલ્સ જોડે છે.

---

## ૫. રોજિંદા જીવનમાં ઉપયોગી પ્રોમ્પ્ટ્સ

- **ડાઉનલોડ્સ ફોલ્ડર સાફ કરવા માટે:**  
  *"મારા Downloads ફોલ્ડરમાં રહેલી બધી ફાઈલો તપાસો, પીડીએફ અને ફોટા માટે અલગ ફોલ્ડર બનાવી તેમાં મૂકો."*
- **પીસી સ્પીડ અને રેમ તપાસવા માટે:**  
  *"મારા કમ્પ્યુટરની હેલ્થ તપાસો, કેટલી રેમ વપરાઈ રહી છે તે Desktop/pc_status.txt માં સેવ કરો."*
- **ઈન્ટરનેટ પરથી રિસર્ચ કરવા માટે:**  
  *"ઈન્ટરનેટ પરથી આ અઠવાડિયાના ટોચના ટેકનોલોજી સમાચારો શોધો અને ડેસ્કટોપ પર સેવ કરો."*
- **અવાજ સાંભળવા માટે:**  
  *"અવાજમાં બોલો: શુભ સવાર! તમારું કમ્પ્યુટર સુરક્ષિત છે."*

---

## ૬. API Key વગર ૧૦૦% ફ્રી અને ઑફલાઇન

તમારે કોઈ પૈસા ચૂકવવાની કે ક્રેડિટ કાર્ડ નાખવાની જરૂર નથી:
1. **Rule Engine:** હેલ્પર-AI માં પહેલેથી જ સ્માર્ટ એન્જિન છે જે સામાન્ય કમાન્ડ્સ API Key વગર જ ચલાવે છે.
2. **Ollama:** તમે ફ્રીમાં [Ollama](https://ollama.com/) ડાઉનલોડ કરી શકો છો જે તમારા પોતાના કમ્પ્યુટર પર પ્રાઈવેટ AI ચલાવે છે.
3. **Google Gemini (ઓપ્શનલ):** જો તમારે ગૂગલનું AI વાપરવું હોય, તો [Google AI Studio](https://aistudio.google.com/) પરથી ફ્રી કી મેળવી `.env` ફાઈલમાં મૂકી શકો છો.

---

## ૭. સુરક્ષા અને ૧-ક્લિક મંજૂરી

જ્યારે Safe Mode ચાલુ હોય:
- જો એજન્ટ સોશિયલ મીડિયા પર કોઈ પોસ્ટ કરવા જશે કે ફાઈલ ડિલીટ કરવા જશે, તો તે અટકી જશે અને સ્ક્રીન પર મંજૂરી માગશે:  
  *`"શું તમે આ પોસ્ટ પબ્લિશ કરવા માંગો છો? [હા] / [ના]"`*
- તમારી મંજૂરી વગર કંઈ પણ થશે નહીં!

---

## ૮. વારંવાર પૂછાતા પ્રશ્નો (FAQ)

### પ્રશ્ન ૧: શું Helper-AI તદ્દન ફ્રી છે?
**હા!** તે ઓપન સોર્સ (MIT License) સોફ્ટવેર છે અને કાયમ માટે ફ્રી છે.

### પ્રશ્ન ૨: start.bat ખોલતાં જ તરત બંધ થઈ જાય છે?
**ઉકેલ:** પાયથોન ઇન્સ્ટોલ કરતી વખતે "Add python.exe to PATH" ચેકબોક્સ સિલેક્ટ કરેલું હોવું જોઈએ. પાયથોન ફરી ઇન્સ્ટોલ કરી એ ચેકબોક્સ ટીક કરો.

### પ્રશ્ન ૩: ચાલુ કામ અટકાવવું હોય તો?
ડેશબોર્ડ પર રહેલું લાલ રંગનું **`⏹ Stop Agent`** બટન દબાવો, એજન્ટ તરત જ કામ અટકાવી દેશે.
