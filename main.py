"""
AI Intelligence Unit Bot
Powered by Perplexity Sonar and Aiogram 3.x

This bot provides real-time research capabilities:
- Fact Verification (/factcheck)
- CVE Vulnerability Research (/cve)
- Company OSINT (/osint)
"""

import asyncio
import logging
import os
import re
import aiohttp
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message, LinkPreviewOptions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# Configuration
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "sonar"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Router
router = Router()

async def query_perplexity(user_text: str, system_prompt: str) -> str:
    """
    Sends a request to the Perplexity API with the given user text and system prompt.
    """
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(PERPLEXITY_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # Extract content from the response
                    content = data['choices'][0]['message']['content']
                    
                    # cleanup for Telegram HTML compatibility
                    content = content.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
                    
                    # Fix common LLM Markdown leaks (Convert **bold** to <b>bold</b>)
                    content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
                    content = re.sub(r'__(.*?)__', r'<u>\1</u>', content)
                    
                    # Remove potential markdown code blocks and conversational filler logic if needed
                    content = content.replace("```html", "").replace("```", "").strip()
                    
                    # Remove forbidden top-level HTML tags that LLM might include
                    content = re.sub(r'^<html.*?>', '', content, flags=re.IGNORECASE).strip()
                    content = re.sub(r'</html>$', '', content, flags=re.IGNORECASE).strip()
                    content = re.sub(r'^<!DOCTYPE html>', '', content, flags=re.IGNORECASE).strip()
                    
                    if content.lower().startswith("html"):
                         content = content[4:].strip()

                    return content
                else:
                    error_text = await response.text()
                    logger.error(f"API Error: {response.status} - {error_text}")
                    return f"⚠️ API Error: {response.status}. Please try again later."
    except Exception as e:
        logger.error(f"Exception during API call: {e}")
        return "⚠️ A network error occurred while contacting the AI service."

def get_input_text(message: Message, command: str) -> str | None:
    """
    Extracts input text from a message.
    Supports both direct arguments (/cmd text) and replies.
    """
    if message.reply_to_message and message.reply_to_message.text:
        return message.reply_to_message.text
    
    if message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            return parts[1]
            
    return None

@router.message(Command("start", "help"))
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

@router.message(Command("factcheck"))
async def cmd_factcheck(message: Message):
    user_input = get_input_text(message, "factcheck")
    
    if not user_input:
        await message.reply(
            "ℹ️ <b>Usage:</b>\n"
            "1. Reply to a message with <code>/factcheck</code>\n"
            "2. Or type <code>/factcheck &lt;claim to verify&gt;</code>",
            parse_mode="HTML"
        )
        return

    # Notify user that processing is happening
    status_msg = await message.reply("🔎 <i>Verifying facts...</i>", parse_mode="HTML")

    system_prompt = (
        "You are an Unbiased Data Analyst. "
        "Your goal is to extract factual truth, ignoring the user's tone, vocabulary, insults, or slang. "
        "Interpret slang as a factual query about the subject (e.g., 'is he gay?', 'is he a criminal?').\n"
        "RULES:\n"
        "1. DO NOT lecture the user. DO NOT mention that the language is offensive. "
        "2. DO NOT output conversational filler (e.g., 'I understand...', 'Here is the result...'). "
        "3. OUTPUT ONLY THE RESPONSE IN HTML FORMAT. DO NOT USE MARKDOWN (no **bold**).\n"
        "4. Detect the user's language (Russian/English) and reply in the SAME language.\n"
        "5. SOURCES SECTION MUST CONTAIN ONLY LINKS. No text explanations in the sources block.\n\n"
        "Output Template:\n"
        "🎯 <b>Verdict</b>: [TRUE / FALSE / UNVERIFIED]\n"
        "📝 <b>Fact</b>: [Dry facts only without moralizing. Citations as [1], [2].]\n"
        "<blockquote expandable><b>Sources</b>:\n- [Link 1 Title] (URL)\n- [Link 2 Title] (URL)</blockquote>"
    )

    response = await query_perplexity(user_input, system_prompt)
    
    # Edit the status message or reply if edit fails (simple reply here for robustness)
    await status_msg.delete()
    await message.reply(response, parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True))

@router.message(Command("cve"))
async def cmd_cve(message: Message):
    user_input = get_input_text(message, "cve")
    
    if not user_input:
        await message.reply(
            "ℹ️ <b>Usage:</b>\n"
            "1. Reply to a message with <code>/cve</code>\n"
            "2. Or type <code>/cve &lt;CVE-ID or Technology Name&gt;</code>",
            parse_mode="HTML"
        )
        return

    status_msg = await message.reply("🛡️ <i>Scanning vulnerability database...</i>", parse_mode="HTML")

    system_prompt = (
        "You are a Cybersecurity Analyst. The user input contains a CVE ID or a technology name.\n"
        "Search for the latest vulnerability data.\n"
        "RULES:\n"
        "1. DO NOT output conversational filler.\n"
        "2. OUTPUT ONLY THE RESPONSE IN HTML FORMAT. DO NOT USE MARKDOWN.\n"
        "3. Detect the user's language (Russian/English) and reply in the SAME language.\n"
        "4. SOURCES SECTION MUST CONTAIN ONLY LINKS. No text explanations in the sources block.\n\n"
        "Output Template:\n"
        "1. 🛡️ <b>Vulnerability</b>: Name/ID.\n"
        "2. 📉 <b>Severity</b>: CVSS Score (if available).\n"
        "3. 💥 <b>Exploits</b>: Publicly available? (Yes/No).\n"
        "4. 💊 <b>Mitigation</b>: How to fix. Use [1], [2] format for citations.\n"
        "<blockquote expandable><b>Sources</b>:\n- [Link 1 Title] (URL)\n- [Link 2 Title] (URL)</blockquote>"
    )

    response = await query_perplexity(user_input, system_prompt)
    
    await status_msg.delete()
    await message.reply(response, parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True))

@router.message(Command("osint"))
async def cmd_osint(message: Message):
    user_input = get_input_text(message, "osint")
    
    if not user_input:
        await message.reply(
            "ℹ️ <b>Usage:</b>\n"
            "1. Reply to a message with <code>/osint</code>\n"
            "2. Or type <code>/osint &lt;Company Name&gt;</code>",
            parse_mode="HTML"
        )
        return

    status_msg = await message.reply("🕵️‍♂️ <i>Gathering intelligence...</i>", parse_mode="HTML")

    system_prompt = (
        "You are a Business Intelligence Analyst. Extract the company name from the user's input "
        "(ignore words like 'check', 'find', 'who is').\n"
        "RULES:\n"
        "1. DO NOT output conversational filler.\n"
        "2. OUTPUT ONLY THE RESPONSE IN HTML FORMAT. DO NOT USE MARKDOWN.\n"
        "3. Detect the user's language (Russian/English) and reply in the SAME language.\n"
        "4. SOURCES SECTION MUST CONTAIN ONLY LINKS. No text explanations in the sources block.\n\n"
        "Output Template:\n"
        "- <b>Industry</b>: Key focus.\n"
        "- <b>Leadership</b>: CEO/Founders.\n"
        "- <b>Tech Stack</b>: Main technologies used.\n"
        "- <b>Latest News</b>: Recent headlines (last 6 months). Use [1], [2] format for citations.\n"
        "<blockquote expandable><b>Sources</b>:\n- [Link 1 Title] (URL)\n- [Link 2 Title] (URL)</blockquote>"
    )

    response = await query_perplexity(user_input, system_prompt)
    
    await status_msg.delete()
    await message.reply(response, parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True))

async def main():
    if not TELEGRAM_BOT_TOKEN or not PERPLEXITY_API_KEY:
        logger.error("❌ Error: TELEGRAM_BOT_TOKEN and PERPLEXITY_API_KEY must be set in .env file.")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    
    # Register router
    dp.include_router(router)

    logging.info("🚀 Bot is starting...")
    
    # Delete webhook to ensure long polling works (optional, but good practice for dev)
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
