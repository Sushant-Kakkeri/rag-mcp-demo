# 🧠 RAG + MCP Smart Assistant

> **An intelligent AI assistant that automatically decides whether to search your uploaded documents or call live tools — built with Python, LangChain, FAISS, and OpenAI GPT-4o.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sushant-kakkeri-rag-mcp-demo-app-l6efgh.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2.16-green)](https://python.langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-red)](https://platform.openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [What This App Does](#-what-this-app-does)
- [Live Demo](#-live-demo)
- [How It Works](#-how-it-works)
- [The Three Tabs](#-the-three-tabs)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Usage Guide](#-usage-guide)
- [The Smart Router Explained](#-the-smart-router-explained)
- [Chunk Settings Explained](#-chunk-settings-explained)
- [Configuration](#-configuration)
- [Common Questions](#-common-questions)
- [Cost Estimate](#-cost-estimate)
- [Known Limitations](#-known-limitations)
- [Roadmap](#-roadmap)
- [Author](#-author)

---

## 🎯 What This App Does

Most AI assistants have two big problems:

1. **They don't know YOUR documents** — they only know what they were trained on
2. **They don't know what's happening NOW** — their knowledge has a cutoff date

This app solves both problems simultaneously:

| Technique | What it does | Badge |
|-----------|-------------|-------|
| **RAG** (Retrieval Augmented Generation) | Searches your uploaded PDFs by meaning — not keywords | 📄 Blue |
| **MCP** (Model Context Protocol) | Calls live tools — web search, weather, Wikipedia, news | 🔧 Green |
| **BOTH** | Combines document search AND live tools in one answer | 🔄 Orange |

The AI decides automatically which approach to use on **every single question** — no manual switching needed.

---

## 🌐 Live Demo

**Try it now:** [sushant-kakkeri-rag-mcp-demo-app-l6efgh.streamlit.app](https://sushant-kakkeri-rag-mcp-demo-app-l6efgh.streamlit.app)

**GitHub:** [github.com/Sushant-Kakkeri/rag-mcp-demo](https://github.com/Sushant-Kakkeri/rag-mcp-demo)

### Demo Questions to Try

```bash
# 📄 Blue RAG badge — searches your uploaded PDF:
"What does the document say about Lambda functions?"

# 🔧 Green MCP badge — uses live tools:
"What is the weather in San Antonio right now?"

# 🔄 Orange BOTH badge — combines both sources:
"Summarize the document AND find the latest AWS news"
```

> **Tip:** To trigger RAG, use words like `document`, `pdf`, `uploaded`, or `what does it say`. To trigger MCP, use words like `weather`, `news`, `today`, or `latest`.

---

## ⚙️ How It Works

```
User types question
        │
        ▼
   router.py ──── scans keywords ────► is_doc?  ──► RAG: search FAISS
        │                               is_live? ──► MCP: call tools
        │                               both?    ──► RAG + MCP combined
        │
        ▼
   GPT-4o reads context + tools ──────► writes final answer
        │
        ▼
   Badge + answer shown in UI
```

**Stage 1 — router.py decides instantly** (no AI, no cost, milliseconds):
Scans the question for keywords. If it finds doc words → searches FAISS. If it finds live words → passes tools to GPT-4o. This is simple Python string matching.

**Stage 2 — GPT-4o decides intelligently** (AI-powered):
Receives the RAG context and/or TOOLS list. Decides which tool to call, calls it, and writes the final polished answer.

---

## 🗂️ The Three Tabs

### 💬 Tab 1 — Chat Assistant
The main interface. Ask any question and get an intelligent answer with a colored routing badge showing exactly how the AI decided to answer.

### 🔬 Tab 2 — Chunk Inspector *(unique feature)*
See exactly how your PDF was broken into searchable pieces — something most RAG apps never expose.
- **5 statistics**: total chunks, average size, average words, max chunk, total words indexed
- **Browse every chunk** in expandable cards with visual size bars
- **Search by keyword** — filters chunks in real time
- **Filter by source file** when multiple PDFs are uploaded
- **Page number and source** shown for every chunk

### 📋 Tab 3 — Chunk Table *(unique feature)*
The entire FAISS database exposed as an interactive spreadsheet.
- **Sort any column** — chunk number, page, word count, size
- **Search across all columns** simultaneously
- **Filter by source file**
- **Download as CSV** — opens in Excel
- **Download as full text** — all chunk content in one file
- **Summary stats** — rows shown, average words, average characters

---

## 📁 Project Structure

```
rag_mcp_demo/
├── app.py              ← Streamlit UI — 3 tabs, badges, session state (~400 lines)
├── router.py           ← Smart router — keyword detection + GPT-4o calls (~280 lines)
├── rag_engine.py       ← RAG engine — PDF loading, FAISS, chunk access (~220 lines)
├── mcp_tools.py        ← MCP tools — web search, weather, Wikipedia, news (~180 lines)
├── .env                ← Your API key (NEVER commit this!)
├── .gitignore          ← Ensures .env stays out of git
├── requirements.txt    ← All Python dependencies
└── documents/          ← Optional: pre-load PDFs here
```

### File Responsibilities

| File | Role | Key methods |
|------|------|-------------|
| `router.py` | The brain — routes every question | `route_and_respond()` |
| `rag_engine.py` | Document memory — loads and searches PDFs | `load_pdf()`, `search()`, `get_chunks_for_display()` |
| `mcp_tools.py` | Live toolbox — 5 real-world tool functions | `web_search()`, `get_weather()`, `wikipedia_search()` |
| `app.py` | The interface — 3 tabs, badges, session state | Creates engines, wires everything together |

### How They Connect

```
app.py  ──creates──►  RAGEngine  ──held by──►  SmartRouter
app.py  ──creates──►  SmartRouter
app.py  ──calls──────►  router.route_and_respond()  on every message
router  ──calls──────►  rag_engine.search()          when doc question
router  ──imports────►  TOOLS from mcp_tools.py      passes to GPT-4o
router  ──calls──────►  execute_tool()               when GPT-4o requests tool
```

---

## 🛠️ Tech Stack

| Component | Technology | Why This One |
|-----------|-----------|--------------|
| Frontend | [Streamlit](https://streamlit.io/) | Python → web app in hours. No HTML/CSS/JS needed. |
| AI Model | [OpenAI GPT-4o](https://platform.openai.com/) | Best tool-calling reliability and answer quality |
| RAG Framework | [LangChain 0.2.16](https://python.langchain.com/) | PyPDFLoader + TextSplitter + FAISS wrapper |
| Vector Database | [FAISS](https://github.com/facebookresearch/faiss) | In-memory, fast, no server needed |
| PDF Reading | [pypdf](https://pypdf.readthedocs.io/) | Pure Python — works on Streamlit Cloud |
| Web Search | [DuckDuckGo](https://duckduckgo.com/) | Free, no API key, no rate limits |
| Weather | [wttr.in](https://wttr.in/) | Free public API, no authentication |
| Encyclopedia | [Wikipedia Python lib](https://wikipedia.readthedocs.io/) | Free, no API key |
| Data | [pandas](https://pandas.pydata.org/) | Powers the Chunk Table tab |
| Deployment | [Streamlit Cloud](https://streamlit.io/cloud) | Free hosting, GitHub auto-deploy |

> **Why FAISS over ChromaDB?** ChromaDB has dependency conflicts with Python 3.14 on Streamlit Cloud. FAISS is simpler, faster, and has no server requirements.

> **Why pypdf over PyMuPDF?** PyMuPDF requires C compilation which fails on Streamlit Cloud. pypdf is pure Python — works everywhere.

> **Why LangChain 0.2.16 specifically?** LangChain changes its API between versions. Pin to 0.2.16 for stable behavior.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- An [OpenAI API key](https://platform.openai.com/api-keys) (pay-as-you-go, ~$5 credit to start)

### 1. Clone the Repository

```bash
git clone https://github.com/Sushant-Kakkeri/rag-mcp-demo.git
cd rag-mcp-demo
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** If you get a FAISS error locally, run: `pip install faiss-cpu`

### 3. Set Up Your API Key

Create a `.env` file in the project root:

```bash
# .env
OPENAI_API_KEY=your-openai-api-key-here
```

> ⚠️ **CRITICAL:** Never commit your `.env` file. It is already listed in `.gitignore`. If you accidentally expose your key, rotate it immediately at [platform.openai.com](https://platform.openai.com/api-keys).

### 4. Run the App

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

### 5. Deploy to Streamlit Cloud (Optional)

1. Push your code to GitHub (ensure `.env` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add your OpenAI API key in **Settings → Secrets**:
   ```toml
   OPENAI_API_KEY = "your-key-here"
   ```
5. Click **Deploy** — your app goes live automatically

---

## 📖 Usage Guide

### Step 1 — Enter your API Key
Paste your OpenAI API key in the sidebar. It reads from `.env` automatically if set.

### Step 2 — Upload a PDF
Click **Browse files** in the sidebar. Upload one or more PDFs. Wait for the success message showing the chunk count (e.g. `✅ document.pdf — 142 chunks`).

### Step 3 — Ask Questions

| Question type | What to say | Badge |
|--------------|-------------|-------|
| About your document | "What does the **document** say about X?" | 📄 Blue RAG |
| Live weather | "What's the weather in Austin **today**?" | 🔧 Green MCP |
| Latest news | "Find the **latest** news about X" | 🔧 Green MCP |
| Wikipedia lookup | "**Search** Wikipedia for X" | 🔧 Green MCP |
| Combined | "Summarize the **document** AND **find** recent news" | 🔄 Orange BOTH |

### Step 4 — Explore the Chunks
Switch to **Tab 2 (Chunk Inspector)** to see how your PDF was broken into searchable pieces. Switch to **Tab 3 (Chunk Table)** for the full spreadsheet view and CSV export.

---

## 🧠 The Smart Router Explained

All routing logic lives in `router.py`. Here is the exact decision process:

```python
# Step 1 — keyword lists define what triggers what
doc_keywords  = ["document", "pdf", "file", "uploaded", "what does it say", ...]
live_keywords = ["weather", "news", "today", "latest", "now", "search", ...]
both_keywords = [" and find ", " and search ", " plus find ", ...]

# Step 2 — scan the question
is_doc  = any(kw in query.lower() for kw in doc_keywords)
is_live = any(kw in query.lower() for kw in live_keywords)

# Step 3 — only search FAISS if actually needed
rag_context = self.rag_engine.search(query) if is_doc else None

# Step 4 — only pass tools to GPT-4o if live data needed
tools = TOOLS if (is_live or not is_doc) else None

# Step 5 — badge label
tool_used = "BOTH" if (is_doc and used_tool) else "RAG" if is_doc else "MCP"
```

**Important:** If a question contains no trigger words (e.g. "what are the moons of Mars?"), the router defaults to MCP even if documents are uploaded. To force RAG, add a doc keyword: "what does the **document** say about Mars moons?"

---

## 🔬 Chunk Settings Explained

Chunk settings are in `rag_engine.py` at line 42:

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,    # max characters per chunk (~150 words)
    chunk_overlap=200   # shared characters between adjacent chunks
)
```

| Parameter | Our Value | LangChain Default | Why We Changed It |
|-----------|----------|------------------|------------------|
| `chunk_size` | **1000** | 4000 | More precise search. Smaller = more focused results. |
| `chunk_overlap` | **200** | 200 | Unchanged. Prevents answers being cut at boundaries. |
| `k` (results) | **4** | — | Top 4 chunks retrieved per query. |

**Why chunks are often smaller than 1000 characters:**
- Short pages (title pages, table of contents rows) have fewer than 1000 chars
- Natural paragraph breaks stop the splitter before the limit
- Section headings are standalone short blocks
- Leftover text at the end of a page is less than 1000 chars

This is normal. An average utilization of 70–75% of the maximum is expected for mixed-content documents.

**Memory usage:** ~7KB per chunk. A 35-page PDF → ~142 chunks → ~1MB RAM.

---

## ⚙️ Configuration

### Changing Chunk Size

Edit `rag_engine.py` line 42:

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,    # smaller = more precise but less context per chunk
    chunk_overlap=100
)
```

### Adding a New Trigger Keyword

Edit `router.py` lines 18–26:

```python
doc_keywords = [
    "document", "pdf", "file", "uploaded",
    "what does it say", "guide", "manual",
    "your new keyword here"    # ← add here
]
```

### Adding a New MCP Tool

**Step 1** — Add the function in `mcp_tools.py`:

```python
def my_new_tool(query: str) -> str:
    """Describe what this tool does — GPT-4o reads this description"""
    result = # your API call here
    return result
```

**Step 2** — Add its definition to the `TOOLS` list:

```python
{
    "type": "function",
    "function": {
        "name": "my_new_tool",
        "description": "What this tool does and when GPT-4o should use it",
        "parameters": {
            "properties": {
                "query": {"type": "string", "description": "The query"}
            },
            "required": ["query"]
        }
    }
}
```

### Changing the System Prompt

Edit `router.py` in the `_build_messages()` method. The system prompt controls GPT-4o's persona and instructions:

```python
system_prompt = """You are a helpful AI assistant for [YOUR ORGANIZATION].
You help [YOUR USERS] by answering questions from uploaded documents.
When citing information, reference the specific page number and document name.
If documents contain conflicting information, note both versions."""
```

---

## ❓ Common Questions

**Q: Why did my question use MCP when I wanted RAG?**
Add a doc keyword to your question. Instead of "what are the satellites of Mars?", ask "what does the **document** say about the satellites of Mars?"

**Q: What happens when I upload two contradictory documents?**
Both are stored in the same FAISS index. If both contradictory chunks rank in the top 4 results, GPT-4o sees both and usually flags the conflict, telling you which document said what. The source filename is preserved in every chunk's metadata.

**Q: What happens to my documents when I close the browser?**
Everything is cleared. FAISS is in-memory only — nothing is stored permanently. Re-upload your documents at the start of each session.

**Q: Does OpenAI see my full documents?**
No. Only the 4 most relevant chunks (~4000 characters) are sent to OpenAI per question. The rest of the document stays in your local FAISS store. OpenAI's API terms state that API data is not used for training.

**Q: Can I upload multiple PDFs?**
Yes. All PDFs merge into the same FAISS index. Each chunk keeps its source filename and page number so you always know which document an answer came from.

**Q: Which makes the routing decision — router.py or GPT-4o?**
Both, at different stages. `router.py` decides **what data to fetch** (instant, no cost, keyword matching). GPT-4o decides **which tool to call** and **writes the final answer** (AI-powered, costs money). They are partners, not competitors.

**Q: Why does FAISS store smaller chunks than the 1000-character limit?**
1000 chars is a maximum, not a target. The splitter stops at 1000 characters OR at a natural break point (paragraph, line break) — whichever comes first. Short pages and section headings create small chunks. An average of 700–800 chars is normal.

**Q: Why can't I use this with sensitive judicial documents right now?**
The current deployment is on Streamlit Cloud which is publicly accessible by URL. For truly sensitive documents, you would need authentication, Azure OpenAI (for data residency guarantees), and private deployment. These are all on the roadmap.

---

## 💰 Cost Estimate

| Action | Cost |
|--------|------|
| Upload a 35-page PDF (embedding) | ~$0.002 total |
| RAG question (4 chunks + answer) | ~$0.01–0.02 |
| MCP question (tool + answer) | ~$0.01–0.03 |
| BOTH question (combined) | ~$0.02–0.04 |
| Web search (DuckDuckGo) | Free |
| Weather (wttr.in) | Free |
| Wikipedia lookup | Free |
| News search | Free |
| Streamlit Cloud hosting | Free |

For 100 questions/day: approximately **$1–4/day** or **$30–120/month**.

---

## ⚠️ Known Limitations

| Limitation | Impact | Planned Fix |
|-----------|--------|-------------|
| In-memory storage only | Documents lost on browser close | PostgreSQL + pgvector |
| Keyword-based routing | Questions without trigger words default to MCP | GPT-4o routing decision |
| No authentication | Any user with the URL can access | Streamlit auth layer |
| PDF only | Word, Excel, PowerPoint not supported | Add LangChain loaders |
| No streaming | Full answer appears at once | `stream=True` in OpenAI call |
| No monitoring | No visibility into costs or errors | LangSmith integration |
| Contradictory documents | Both stored together, no priority | Document versioning + metadata |

---

## 🗺️ Roadmap

**Immediate (next 30 days)**
- [ ] Streaming responses — words appear as AI thinks
- [ ] LangSmith monitoring — trace every AI call with cost and latency
- [ ] Role-based system prompts — sidebar selector (Judge / Clerk / Attorney)
- [ ] Judiciary-specific document library — real court procedures and policies

**Short Term (1–3 months)**
- [ ] PostgreSQL + pgvector — persistent storage across sessions
- [ ] User authentication — login/logout with role-based access
- [ ] Multi-format support — Word, Excel, web pages
- [ ] Document versioning — tag with version and date

**Long Term (3–12 months)**
- [ ] LangGraph multi-agent workflows
- [ ] Azure OpenAI — enterprise data residency
- [ ] AWS/Azure deployment — enterprise-grade hosting
- [ ] RAGAS evaluation — automated RAG quality testing
- [ ] Integration with existing court systems

---

## 📦 Requirements

```txt
streamlit
openai
langchain==0.2.16
langchain-openai==0.1.23
langchain-community==0.2.16
langchain-text-splitters==0.2.4
langchain-core==0.2.38
faiss-cpu
pypdf
python-dotenv
requests
duckduckgo-search
wikipedia
pandas
```

---

## 🔐 Security Notes

- **API Key** — Stored in `.env` locally, encrypted Streamlit Secrets in production. Never in source code.
- **`.gitignore`** — The `.env` file is excluded from git. Check this before your first commit.
- **Document storage** — All documents stored in RAM only. Nothing written to disk permanently.
- **OpenAI exposure** — Only 4 relevant chunks sent per question, not the full document.
- **Session isolation** — Each browser session has its own independent FAISS store.

---

## 👨‍💻 Author

**Sushant Kakkeri**
Senior Enterprise Software Engineer

- **GitHub:** [@Sushant-Kakkeri](https://github.com/Sushant-Kakkeri)
- **App 1 (RAG + MCP):** [sushant-kakkeri-rag-mcp-demo.streamlit.app](https://sushant-kakkeri-rag-mcp-demo-app-l6efgh.streamlit.app)
- **App 2 (Research Assistant):** [github.com/Sushant-Kakkeri/research-assistant](https://github.com/Sushant-Kakkeri/research-assistant)

---

## 📄 License

This project is licensed under the MIT License.

---

*Built with Python · LangChain · FAISS · OpenAI GPT-4o · Streamlit · © 2026 Sushant Kakkeri*
