
----it's the one built for people who can't read logs, not the one built for engineers who want faster log reading.----

PulpGulp - "Logs are unstructured. They're too big for local LLM context windows. PulpGulp chunks them intelligently, processes each chunk, and merges the results into a single coherent narrative. Enterprise tools solve this at scale. PulpGulp solves it locally, for free, on your own hardware."
Stop burning Claude usage on massive system logs.
PulpGulp is a Windows desktop app that condenses large system logs using your local LLM, so you can paste the condensed output to Claude (or any AI assistant) without hitting usage limits or losing critical diagnostic info.
Built for vibe coders who generate walls of error logs and need to get them into Claude fast.
---
How It Works
Load or paste your log (drag-drop, browse, or paste directly)
Pick a condensing level — Light (cleanup), Normal (diagnostic narrative), or Heavy (errors only)
Hit Condense — PulpGulp chunks the log, sends each chunk to your local LLM, then merges the results into one coherent document
Copy the output and paste it to Claude
Everything runs locally. No cloud APIs. No data leaves your machine.
---
Features
Two input modes — Load File (drag-drop or browse) and Paste Text (toggle between them)
Three condensing levels — Light / Normal / Heavy depending on how aggressive you want the reduction
Smart chunking — Splits large logs into configurable chunks (default 500 lines), processes each, then hierarchically merges
Live progress — Smooth progress bar and streaming terminal output as chunks complete
Output stats — Shows original lines, condensed lines, and reduction percentage
Connection monitoring — Green/red status dot, auto-checks LM Studio every 10 seconds
Output actions — Copy to Clipboard, Save File, or Show in Folder
---
Requirements
Windows 10/11
LM Studio — download here
A local LLM loaded in LM Studio — tested with Qwen 3.6-27B Instruct (Q6_K), but any model with decent instruction-following works
Python 3.10+ (if running from source)
---
Quick Start (from source)
```bash
# Clone the repo
git clone https://github.com/dennyvgeorge/PulpGulp.git
cd PulpGulp

# Install dependencies
pip install -r requirements.txt

# Start LM Studio and load a model, then start the local server (default port 1234)

# Run PulpGulp
python pulpgulp.py
```
---
Quick Start (pre-built .exe)
Download the latest release, extract the folder, and run `PulpGulp.exe`. Make sure LM Studio is running with a model loaded and the local server started on port 1234.
---
Project Structure
```
PulpGulp/
├── pulpgulp.py              # Entry point (splash → main window)
├── requirements.txt          # PyQt6, requests, chardet
├── gen_test.py               # Test log generator (5000 lines)
├── src/
│   ├── api_client.py         # LM Studio API client (connection check, retry logic)
│   ├── chunker.py            # File reading, encoding detection, chunking, stats
│   ├── condenser.py          # Per-chunk extraction + hierarchical merge
│   ├── main_window.py        # PyQt6 main window (all UI states)
│   ├── prompts.py            # Light/Normal/Heavy system prompts + merge prompt
│   ├── splash_screen.py      # Splash screen with fade-out
│   ├── styles.py             # Complete stylesheet (dark theme)
│   └── worker.py             # QThread worker with progress signals
└── assets/
    ├── logo_header.png       # Main window logo
    └── splash.png            # Splash screen image
```
---
How It's Built
PulpGulp was built using a three-tier AI workflow:
Gemini — brainstorming and architecture review
Claude — execution planning, architecture decisions, exact code generation
Qwen 3.6-27B (via Aider + LM Studio) — local code typist executing Claude's instructions
The UI was designed in Adobe Illustrator and implemented in PyQt6 with a custom dark theme.
---
License
MIT — do whatever you want with it.
