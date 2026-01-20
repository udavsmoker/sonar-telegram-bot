from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, LinkPreviewOptions
from telesonar.utils.text import get_input_text
from telesonar.services.perplexity import query_perplexity

research_router = Router()

@research_router.message(Command("factcheck"))
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
    
    await status_msg.delete()
    await message.reply(response, parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True))

@research_router.message(Command("cve"))
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

@research_router.message(Command("osint"))
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
