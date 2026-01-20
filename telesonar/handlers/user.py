from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

user_router = Router()

@user_router.message(Command("start", "help"))
async def cmd_welcome(message: Message):
    welcome_text = (
        "<b>AI Intelligence Unit</b>\n"
        "I execute real-time research using the <b>Perplexity Sonar</b> engine.\n\n"
        "<b>📁 Capabilities</b>\n\n"
        "🔹 <code>/factcheck</code> — <b>Fact Verification</b>\n"
        "Validates statements against authoritative sources.\n"
        "<i>Usage: Reply or /factcheck [statement]</i>\n\n"
        "🔹 <code>/cve</code> — <b>Vulnerability Scanner</b>\n"
        "Retrieves severity, exploits, and mitigation strategies.\n"
        "<i>Usage: /cve [CVE-ID] or [Tech Name]</i>\n\n"
        "🔹 <code>/osint</code> — <b>Corporate Profiling</b>\n"
        "Generates dossiers on leadership, tech stack, and news.\n"
        "<i>Usage: /osint [Company Name]</i>"
    )
    await message.answer(welcome_text, parse_mode="HTML")
