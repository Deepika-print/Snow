<div align="center">

<h1>❄️ Snow</h1>
<p><strong>Autonomous AI Agent — Powered by Groq + LLaMA 3.3 70B</strong></p>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=for-the-badge)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Gradio](https://img.shields.io/badge/UI-Gradio-orange?style=for-the-badge)](https://gradio.app)

<p>Give Snow any task — it searches the web, executes code, reads and writes files, and delivers results <strong>autonomously</strong>.</p>

</div>

---

## 🎥 Demo

> Coming soon — deploying to Hugging Face Spaces

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 Web Search | Real-time DuckDuckGo search for current information |
| 🌐 Web Scraping | Read full content of any webpage |
| 🐍 Python Execution | Write and run Python code autonomously |
| ⚡ Shell Commands | Execute system commands with safety filters |
| 📁 File I/O | Create, read, and modify files |
| 💬 WhatsApp Bot | Send Snow tasks via WhatsApp using Twilio |
| 🛡️ Security | Input validation, prompt injection detection, rate limiting |
| 🧠 Two-Model Strategy | Fast tool calling + high quality final answers |

---

## 🧠 How It Works

```
User Task
    ↓
Security Validation (prompt injection check, length limit)
    ↓
Agent Loop (llama-3.1-8b-instant — tool calling)
    ↓
Tools: web_search → scrape_webpage → run_python → write_file
    ↓
Final Answer (llama-3.3-70b-versatile — high quality response)
    ↓
User
```

Snow uses a **two-model strategy**:
- `llama-3.1-8b-instant` — fast, reliable tool calling
- `llama-3.3-70b-versatile` — high quality final answers

---

## 🗂️ Project Structure

```
Snow/
├── app.py            — Gradio web UI (dark terminal aesthetic)
├── agent.py          — Core agent loop with security validation
├── tools.py          — All tools: search, scrape, code, files
├── whatsapp_bot.py   — WhatsApp interface via Twilio + Flask
├── requirements.txt  — Dependencies
└── .env.example      — Environment variables template
```

---

## 🚀 Quick Start

### 1. Clone & install
```bash
git clone https://github.com/Deepika-print/Snow.git
cd Snow
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### 2. Set up environment
Create a `.env` file:
```env
GROQ_API_KEY=your_groq_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_NUMBER=+14155238886
```

Get your free Groq API key at [console.groq.com](https://console.groq.com)

### 3. Run the web UI
```bash
python app.py
```
Open http://127.0.0.1:7860

### 4. Run WhatsApp bot (optional)
```bash
# Terminal 1
python whatsapp_bot.py

# Terminal 2
ngrok http 5000
```
Set Twilio webhook to: `https://your-ngrok-url/whatsapp`

---

## 🛡️ Security Features

- **Input validation** — blocks empty tasks and tasks over 2000 characters
- **Prompt injection detection** — detects and blocks jailbreak attempts
- **Shell command filtering** — blocks dangerous commands like `rm -rf`
- **Python execution sandbox** — 30 second timeout, blocks dangerous imports
- **Automatic fallback** — if tool calling fails, answers directly without crashing

---

## 📦 Tech Stack

| Component | Technology |
|---|---|
| LLM | Groq API (LLaMA 3.1 8B + 3.3 70B) |
| Web Search | DuckDuckGo (ddgs) |
| Web Scraping | BeautifulSoup4 + requests |
| Web UI | Gradio |
| WhatsApp | Twilio + Flask |
| Tunneling | ngrok |

---

## 💡 Example Tasks

```
Search for the latest AI news today and summarize the top 5 stories
Write a Python script that generates a Fibonacci sequence up to 1000
Who is the current Prime Minister of India? Search and give details
Search for the best free resources to learn React in 2026
```

---

## 📄 License

MIT — Built with ❄️ by [Deepika Singh](https://github.com/Deepika-print)
