import re
from bs4 import BeautifulSoup
import math

def calculate_reading_time(text: str) -> int:
    """Calculates approximate reading time in minutes (200 words/min)."""
    words = len(text.split())
    minutes = math.ceil(words / 200)
    return max(1, minutes)

def clean_html_to_markdown(html_content: str) -> str:
    """
    Cleans raw HTML, strips scripts, styles, iframes, navbars, and cookie popups,
    and converts text to clean structured Markdown with preserved headers, code, and links.
    """
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    # Remove non-content tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "noscript", "svg"]):
        tag.decompose()

    # Convert headers
    for i in range(6, 0, -1):
        for header in soup.find_all(f"h{i}"):
            header_text = header.get_text().strip()
            if header_text:
                header.replace_with(f"\n\n{'#' * i} {header_text}\n\n")

    # Convert code blocks
    for pre in soup.find_all("pre"):
        code_text = pre.get_text()
        pre.replace_with(f"\n\n```\n{code_text}\n```\n\n")

    # Convert inline code
    for code in soup.find_all("code"):
        if code.parent and code.parent.name != "pre":
            code.replace_with(f"`{code.get_text()}`")

    # Convert links
    for a in soup.find_all("a", href=True):
        link_text = a.get_text().strip()
        href = a["href"]
        if link_text and not href.startswith("javascript:"):
            a.replace_with(f"[{link_text}]({href})")

    # Convert bold / strong
    for strong in soup.find_all(["strong", "b"]):
        text = strong.get_text().strip()
        if text:
            strong.replace_with(f"**{text}**")

    # Convert list items
    for li in soup.find_all("li"):
        li_text = li.get_text().strip()
        if li_text:
            li.replace_with(f"\n* {li_text}")

    # Convert paragraphs
    for p in soup.find_all("p"):
        p_text = p.get_text().strip()
        if p_text:
            p.replace_with(f"\n\n{p_text}\n\n")

    text = soup.get_text()
    
    # Normalize excess newlines and whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text
