# TeleSonar AI 📡

A lightweight, no-nonsense intelligence bot for Telegram.  
Powered by **Perplexity Sonar** and **real-time web scraping**.

Designed for developers, analysts, and skeptics who need facts, not hallucinations.

## ⚡ Capabilities

### AI Research (Perplexity Sonar)

| Command | Description |
|---------|-------------|
| `/factcheck` | Validates claims against authoritative sources |
| `/cve` | Vulnerability lookup via NVD API (CVE-ID or tech name) |
| `/osint` | Corporate profiling: leadership, tech stack, news |

### Web Scraping

| Command | Description |
|---------|-------------|
| `/trending` | GitHub Trending repos with CSV export |
| `/trending python` | Filter by language |
| `/trending rust weekly` | Filter by language + time range |

**Time ranges:** `daily`, `weekly`, `monthly`

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Aiogram 3.x** — Async Telegram API
- **Perplexity API** — Sonar Model for AI research
- **BeautifulSoup + lxml** — Web scraping
- **Aiohttp** — Async HTTP client

## 🚀 Deployment

### Prerequisites
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- A Perplexity API Key

### Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/telesonar-ai.git
   cd telesonar-ai
   ```

2. **Set up the environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure keys**
   Rename the example config and paste your keys:
   ```bash
   mv .env.example .env
   # Edit .env with your favorite editor
   ```

4. **Launch**
   ```bash
   python run.py
   ```

---

*Built for research purposes. Data provided by LLMs should always be verified.*
