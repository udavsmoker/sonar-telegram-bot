import csv
import io
import logging
import aiohttp
from bs4 import BeautifulSoup
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from telesonar.utils.text import get_input_text

github_router = Router()
logger = logging.getLogger(__name__)

GITHUB_TRENDING_URL = "https://github.com/trending"

async def scrape_github_trending(language: str = None, since: str = "daily"):
    url = GITHUB_TRENDING_URL
    if language:
        url = f"{url}/{language.lower()}"
    
    params = {"since": since}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params, headers=headers, timeout=15) as response:
                if response.status != 200:
                    logger.error(f"GitHub returned {response.status}")
                    return None
                html = await response.text()
        except Exception as e:
            logger.error(f"GitHub scraping error: {e}")
            return None
    
    soup = BeautifulSoup(html, "lxml")
    results = []
    repo_list = soup.find_all("article", class_="Box-row")
    
    if not repo_list:
        logger.warning(f"No repos found. HTML length: {len(html)}")
        return []
    
    for repo in repo_list[:25]:
        try:
            name_tag = repo.find("h2", class_="h3")
            if not name_tag:
                continue
            
            link_tag = name_tag.find("a")
            if not link_tag:
                continue
            
            full_name = link_tag.get("href", "").strip("/")
            repo_url = f"https://github.com/{full_name}"
            
            desc_tag = repo.find("p", class_="col-9")
            description = desc_tag.get_text(strip=True) if desc_tag else ""
            
            lang_tag = repo.find("span", itemprop="programmingLanguage")
            language_name = lang_tag.get_text(strip=True) if lang_tag else "N/A"
            
            stars_tag = repo.find("a", href=lambda x: x and x.endswith("/stargazers"))
            total_stars = stars_tag.get_text(strip=True).replace(",", "") if stars_tag else "0"
            
            stars_today_tag = repo.find("span", class_="d-inline-block float-sm-right")
            stars_period = stars_today_tag.get_text(strip=True) if stars_today_tag else "N/A"
            
            forks_tag = repo.find("a", href=lambda x: x and x.endswith("/forks"))
            forks = forks_tag.get_text(strip=True).replace(",", "") if forks_tag else "0"
            
            results.append({
                "rank": len(results) + 1,
                "name": full_name,
                "url": repo_url,
                "description": description[:200] if description else "",
                "language": language_name,
                "stars": total_stars,
                "forks": forks,
                "stars_period": stars_period
            })
            
        except Exception as e:
            logger.error(f"Error parsing repo: {e}")
            continue
    
    return results


def generate_csv(data: list) -> bytes:
    if not data:
        return b""
    
    output = io.StringIO()
    fieldnames = ["rank", "name", "url", "description", "language", "stars", "forks", "stars_period"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    
    return output.getvalue().encode("utf-8")


@github_router.message(Command("trending"))
async def cmd_trending(message: Message):
    user_input = get_input_text(message, "trending")
    parts = user_input.split() if user_input else []
    language = None
    since = "daily"
    
    if len(parts) >= 1:
        language = parts[0]
    if len(parts) >= 2 and parts[1] in ["daily", "weekly", "monthly"]:
        since = parts[1]
    
    lang_text = language.capitalize() if language else "All Languages"
    status_msg = await message.reply(
        f"🔍 *Scraping GitHub Trending...*\n"
        f"📊 {lang_text} | {since.capitalize()}",
        parse_mode="Markdown"
    )
    
    results = await scrape_github_trending(language, since)
    
    if results is None:
        await status_msg.edit_text("❌ *Error*: Could not connect to GitHub.", parse_mode="Markdown")
        return
    
    if not results:
        await status_msg.edit_text(
            f"No trending repos found for `{language}`.\nTry a different language or check the spelling.",
            parse_mode="Markdown"
        )
        return
    
    csv_data = generate_csv(results)
    filename = f"github_trending_{language or 'all'}_{since}.csv"
    
    preview = [
        f"🚀 <b>GitHub Trending</b>\n"
        f"<i>{lang_text} • {since.capitalize()}</i>\n"
        f"{'─' * 20}\n"
    ]
    
    for repo in results[:5]:
        desc = repo['description'][:80] + "..." if len(repo['description']) > 80 else repo['description']
        desc = desc.replace("<", "&lt;").replace(">", "&gt;")
        
        preview.append(
            f"<b>#{repo['rank']}</b> <a href=\"{repo['url']}\">{repo['name']}</a>\n"
            f"    ⭐ {repo['stars']}  •  🍴 {repo['forks']}  •  {repo['language']}\n"
            f"    <i>{desc}</i>\n\n"
        )
    
    preview.append(f"{'─' * 20}\n📎 <b>{len(results)} repos</b> attached as CSV")
    
    await status_msg.delete()
    
    await message.reply_document(
        document=BufferedInputFile(csv_data, filename=filename),
        caption="".join(preview),
        parse_mode="HTML"
    )
