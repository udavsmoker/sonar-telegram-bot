import aiohttp
import logging
from telesonar.config import PERPLEXITY_API_KEY, PERPLEXITY_URL, PERPLEXITY_MODEL
from telesonar.utils.text import clean_llm_response

logger = logging.getLogger(__name__)

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
                    content = data['choices'][0]['message']['content']
                    return clean_llm_response(content)
                else:
                    error_text = await response.text()
                    logger.error(f"API Error: {response.status} - {error_text}")
                    return f"⚠️ API Error: {response.status}. Please try again later."
    except Exception as e:
        logger.error(f"Exception during API call: {e}")
        return "⚠️ A network error occurred while contacting the AI service."
