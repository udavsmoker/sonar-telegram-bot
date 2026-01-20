from aiogram.types import Message
import re

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

def clean_llm_response(content: str) -> str:
    """
    Cleans raw LLM response for Telegram HTML compatibility.
    Removes forbidden tags, converts markdown, strips code blocks.
    """
    content = re.sub(r'^<!DOCTYPE html>', '', content, flags=re.IGNORECASE).strip()
    content = re.sub(r'<html.*?>', '', content, flags=re.IGNORECASE).strip()
    content = re.sub(r'</html>', '', content, flags=re.IGNORECASE).strip()
    content = re.sub(r'<body.*?>', '', content, flags=re.IGNORECASE).strip()
    content = re.sub(r'</body>', '', content, flags=re.IGNORECASE).strip()
    content = re.sub(r'<head.*?>.*?</head>', '', content, flags=re.IGNORECASE | re.DOTALL).strip()
    
    content = re.sub(r'<p>', '\n', content, flags=re.IGNORECASE)
    content = re.sub(r'</p>', '\n', content, flags=re.IGNORECASE)
    
    unsupported_tags = ['div', 'span', 'section', 'article', 'header', 'footer', 'main', 'nav', 
                        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li']
    for tag in unsupported_tags:
        content = re.sub(f'<{tag}.*?>', '', content, flags=re.IGNORECASE)
        content = re.sub(f'</{tag}>', '', content, flags=re.IGNORECASE)
    
    content = content.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    
    content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
    content = re.sub(r'__(.*?)__', r'<u>\1</u>', content)
    
    content = content.replace("```html", "").replace("```", "").strip()
    
    if content.lower().startswith("html"):
        content = content[4:].strip()
    
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()
