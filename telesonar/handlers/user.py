from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

user_router = Router()

@user_router.message(Command("start", "help"))
async def cmd_welcome(message: Message):
    welcome_text = (
        "📡 <b>TeleSonar AI</b>\n"
        "<i>Real-time intelligence powered by Perplexity Sonar</i>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔍 <b>AI Research</b>\n\n"
        "  <code>/factcheck</code> — Fact Verification\n"
        "  <i>Validates claims against authoritative sources</i>\n\n"
        "  <code>/cve</code> — Vulnerability Scanner\n"
        "  <i>Severity, exploits, and mitigation via NVD</i>\n\n"
        "  <code>/osint</code> — Corporate Profiling\n"
        "  <i>Leadership, tech stack, recent news</i>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📊 <b>Web Scraping</b>\n\n"
        "  <code>/trending</code> — GitHub Trending\n"
        "  <i>Top repos with CSV export</i>\n"
        "  <code>/trending python weekly</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<i>All data should be independently verified.</i>"
    )
    await message.answer(welcome_text, parse_mode="HTML")
