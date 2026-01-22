import json
import logging
import os
import aiohttp
from datetime import datetime
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from telesonar.utils.text import get_input_text

import asyncio

cve_router = Router()
logger = logging.getLogger(__name__)

CACHE_FILE = "data/cve_cache.json"
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading cache: {e}")
        return {}

def save_cache(cache_data):
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving cache: {e}")

async def fetch_cve_from_nvd(keyword: str):
    headers = {"User-Agent": "TeleSonarBot/1.0"}
    params = {"keywordSearch": keyword, "resultsPerPage": 5}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(NVD_API_URL, params=params, headers=headers, timeout=30) as response:
                if response.status == 403:
                    logger.error("NVD API rate limit hit")
                    return None
                if response.status != 200:
                    logger.error(f"NVD API returned {response.status}")
                    return None
                data = await response.json()
        except asyncio.TimeoutError:
            logger.error("NVD API timeout")
            return None
        except Exception as e:
            logger.error(f"NVD API error: {e}")
            return None

    results = []
    vulnerabilities = data.get("vulnerabilities", [])
    
    for vuln in vulnerabilities[:5]:
        cve_data = vuln.get("cve", {})
        cve_id = cve_data.get("id", "Unknown")
        
        descriptions = cve_data.get("descriptions", [])
        description = "No description available"
        for desc in descriptions:
            if desc.get("lang") == "en":
                description = desc.get("value", description)
                break
        
        severity = "N/A"
        metrics = cve_data.get("metrics", {})
        
        for cvss_key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
            if cvss_key in metrics and metrics[cvss_key]:
                cvss_data = metrics[cvss_key][0].get("cvssData", {})
                base_score = cvss_data.get("baseScore", "N/A")
                base_severity = cvss_data.get("baseSeverity", "")
                severity = f"{base_score} ({base_severity})" if base_severity else str(base_score)
                break
        
        results.append({
            "id": cve_id,
            "description": description,
            "severity": severity,
            "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}"
        })
    
    return results

@cve_router.message(Command("cve"))
async def cmd_cve_scrape(message: Message):
    keyword = get_input_text(message, "cve")
    
    if not keyword:
        await message.reply(
            "⚠️ Usage: `/cve <keyword>`\nExample: `/cve apache`",
            parse_mode="Markdown"
        )
        return

    status_msg = await message.reply("🔍 *Searching NVD database...*", parse_mode="Markdown")
    
    cache = load_cache()
    cached_entry = cache.get(keyword.lower())
    
    if cached_entry:
        last_updated = datetime.fromisoformat(cached_entry["timestamp"])
        if (datetime.now() - last_updated).total_seconds() < 86400:
            results = cached_entry["data"]
            logger.info(f"Returning cached results for '{keyword}'")
        else:
            results = await fetch_cve_from_nvd(keyword)
    else:
        results = await fetch_cve_from_nvd(keyword)

    if results is None:
        await status_msg.edit_text("❌ *Error*: Could not connect to NVD database. Try again later.", parse_mode="Markdown")
        return

    if not results:
        await status_msg.edit_text(f"No CVEs found for `{keyword}`.", parse_mode="Markdown")
        return

    cache[keyword.lower()] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }
    save_cache(cache)

    output = [f"🛡 *Top {len(results)} CVE Results for '{keyword}'*\n"]
    
    for item in results:
        desc = item['description'][:150] + "..." if len(item['description']) > 150 else item['description']
        severity = item.get('severity', 'N/A')
        output.append(f"🔹 *[{item['id']}]({item['url']})*\n⚠️ Severity: {severity}\n{desc}\n")

    output.append(f"\n_Source: NVD (NIST)_")
    
    try:
        await status_msg.edit_text("\n".join(output), parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Telegram formatting error: {e}")
        # Fallback for formatting errors
        await status_msg.edit_text(f"Found {len(results)} results, but failed to format them.", parse_mode="Markdown")
