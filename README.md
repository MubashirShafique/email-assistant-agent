# 📧 Email Assistant Agent

An AI-powered email assistant that reads your unread Gmail messages, automatically drafts professional replies using OpenAI, and lets you approve, edit, or reject each reply before it gets sent — all through a clean Streamlit web interface.

---

##  Features

- **Fetch Unread Emails** — Connects to your Gmail inbox via IMAP and retrieves all unread messages.
- **AI-Drafted Replies** — Uses OpenAI (GPT-4o-mini or your chosen model) to automatically write professional, context-aware replies.
- **Human-in-the-Loop Control** — Before any email is sent, you get to review the draft and choose one of three actions:
  - ✅ **Approve** — Send the AI-drafted reply as-is.
  - ✏️ **Edit & Send** — Modify the reply in a text box and send your edited version.
  - ❌ **Reject** — Skip sending a reply for that email.
- **Processes Emails One by One** — Goes through each unread email sequentially so nothing gets missed.
- **Persistent Memory per Email** — Uses LangGraph's `MemorySaver` so each email thread maintains its own state during the session.

---

##  Tech Stack

| Component | Technology |
|-----------|------------|
| UI | Streamlit |
| AI Agent | LangChain + LangGraph |
| LLM | OpenAI (GPT-4o-mini or configurable) |
| Email Sending | Python `smtplib` (Gmail SMTP) |
| Email Reading | Python `imaplib` (Gmail IMAP) |
| Human-in-the-Loop | LangChain `HumanInTheLoopMiddleware` |
| Environment Config | `python-dotenv` |

---

## 📁 Project Structure

```
email-assistant-agent/
│
├── main.py          # Streamlit UI — the main app interface
├── agent.py         # LangChain/LangGraph agent setup with Human-in-the-Loop
├── tools.py         # Tool definitions: read emails, write reply, send email
├── gmail_auth.py    # Gmail SMTP and IMAP authentication helpers
├── .env             # Environment variables (API keys, Gmail credentials)
├── pyproject.toml   # Project metadata and dependencies
├── requirements.txt # Full list of pinned dependencies
└── README.md        # You are here
```

### File Descriptions

**`main.py`**
The Streamlit frontend. Handles the full UI flow: fetching emails, displaying them, running the agent, and showing the approve/edit/reject buttons when the agent pauses for human review.

**`agent.py`**
Sets up the LangGraph agent with two tools (`send_email` and `write_email_reply`) and configures `HumanInTheLoopMiddleware` so the agent automatically pauses and waits for your decision before calling `send_email`.

**`tools.py`**
Contains three core functions:
- `read_unread_emails()` — Fetches all unread emails from Gmail.
- `write_email_reply()` — Uses OpenAI with structured output to generate a subject and body for the reply.
- `send_email()` — Sends an email via Gmail SMTP.

**`gmail_auth.py`**
Provides `get_smtp_connection()` and `get_imap_connection()` — authenticated connections to Gmail for sending and reading emails respectively.

---

## ⚙️ Setup & Installation

### 1. Prerequisites

- Python 3.11 or higher
- A Gmail account with **App Password** enabled (see below)
- An OpenAI API Key

### 2. Clone the Repository

```bash
git clone <your-repo-url>
cd email-assistant-agent
```

### 3. Install Dependencies

Using `pip`:
```bash
pip install -r requirements.txt
```

Or using `uv` (faster):
```bash
uv sync
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory (or fill in the existing one):

```env
GMAIL_USER=your_email@gmail.com
GMAIL_PASSWORD=your_gmail_app_password
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key
```

> **Important:** `GMAIL_PASSWORD` must be a **Gmail App Password**, not your regular Gmail password. See the section below on how to generate one.

### 5. Run the App

```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🔐 Gmail App Password Setup

Since the agent uses SMTP/IMAP to access Gmail directly, you need to generate an App Password:

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required)
3. Go to **Security → App Passwords**
4. Select app: **Mail**, device: **Other** → give it a name like `Email Agent`
5. Copy the generated 16-character password
6. Paste it as `GMAIL_PASSWORD` in your `.env` file

---

##  How It Works — Step by Step

```
User clicks "Read all Unread Emails"
        ↓
App connects to Gmail via IMAP
        ↓
All unread emails are fetched and displayed
        ↓
User clicks "Process & Reply Emails"
        ↓
For each email:
    ├─ Agent calls write_email_reply() to draft a reply
    ├─ Agent attempts to call send_email()
    ├─ HumanInTheLoop middleware PAUSES the agent
    ├─ UI shows the draft reply with Approve / Edit / Reject buttons
    │
    ├─ ✅ Approve → Agent resumes and sends the email as drafted
    ├─ ✏️ Edit   → Agent sends the user's modified version
    └─ ❌ Reject → Agent skips sending, moves to next email
        ↓
Once all emails are processed → Success screen 🎉
```

---

## 🧠 Agent Configuration

The agent in `agent.py` is built with:

- **Model:** Configurable via `OPENAI_MODEL` env variable (default: `gpt-4o-mini`)
- **Tools:** `send_email` and `write_email_reply`
- **Checkpointer:** `MemorySaver` — keeps each email thread's state in memory during the session
- **Middleware:** `HumanInTheLoopMiddleware` configured to interrupt on `send_email` with three allowed decisions: `approve`, `edit`, `reject`

The `write_email_reply` tool does **not** trigger a human interrupt — the agent runs it freely to generate drafts. Only `send_email` requires your approval.

---

##  Dependencies

Key packages used in this project:

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `langchain` | Agent and tool orchestration |
| `langchain-openai` | OpenAI LLM integration |
| `langgraph` | Agent graph with Human-in-the-Loop support |
| `openai` | OpenAI API client |
| `python-dotenv` | Load environment variables from `.env` |
| `pydantic` | Structured output schema for AI replies |

Full pinned versions are listed in `requirements.txt`.

---

## ⚠️ Known Limitations

- **Gmail only** — The current implementation is hardcoded for Gmail's SMTP/IMAP servers. Other email providers would need changes in `gmail_auth.py`.
- **Plain text emails only** — The email reader extracts `text/plain` content. HTML-only emails may appear empty.
- **In-memory state** — `MemorySaver` stores state in RAM. Restarting the app clears all agent memory.
- **Single session** — The app processes one batch of unread emails per session. After completion, it resets automatically.

---


## 📄 License

This project is open source. Feel free to use and modify it for personal or commercial projects.
