# TeleSonar AI 📡

A lightweight, no-nonsense intelligence bot for Telegram.  
Powered by **Perplexity Sonar**, it turns chat messages into actionable research data in seconds.

Designed for developers, analysts, and skeptics who need facts, not hallucinations.

## ⚡ Capabilities

### 1. `/factcheck` – Truth Verification
Validates claims against authoritative web sources. Neutralizes toxic language to focus purely on the factual query.
- **Input:** *"They said the earth is flat"*
- **Output:** Verdict (False), Dry Facts, Citation Links.

### 2. `/cve` – Vulnerability Scanner
Instant lookups for CVE IDs or technology names. Perfect for quick security triage.
- **Returns:** Severity (CVSS), Exploit availability, Mitigation steps.
- **Format:** HTML report with clean foldable sources.

### 3. `/osint` – Corporate Profiling
Generates a quick dossier on any company.
- **Data points:** Leadership, Tech Stack, Industry Focus, Recent News Headlines.

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Aiogram 3.x** (Async Telegram API)
- **Perplexity API** (Sonar Model)
- **Aiohttp** (Async requests)

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
   python main.py
   ```

---

*Built for research purposes. Data provided by LLMs should always be verified.*
