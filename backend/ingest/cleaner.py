import re
import math
import html
from bs4 import BeautifulSoup

def calculate_reading_time(text: str) -> int:
    """Calculates approximate reading time in minutes (200 words/min)."""
    words = len(text.split())
    minutes = math.ceil(words / 200)
    return max(1, minutes)

def clean_html_to_reader_prose(html_content: str) -> str:
    """
    Firefox / Safari Reading Mode Cleaner:
    Strips scripts, styles, iframes, navbars, cookies, and ads.
    Converts text to clean structured Reader Mode prose with NO raw URLs, hrefs, or link brackets.
    """
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    # Remove all non-content tags, ads, trackers, and navigation elements
    for tag in soup([
        "script", "style", "nav", "footer", "header", "aside", "form",
        "iframe", "noscript", "svg", "button", "input", "select", "dialog"
    ]):
        tag.decompose()

    # Convert headers to clean line-separated headers without markdown hashes
    for i in range(6, 0, -1):
        for header in soup.find_all(f"h{i}"):
            header_text = header.get_text().strip()
            if header_text:
                header.replace_with(f"\n\n{header_text}\n\n")

    # Convert code blocks
    for pre in soup.find_all("pre"):
        code_text = pre.get_text().strip()
        if code_text:
            pre.replace_with(f"\n\n{code_text}\n\n")

    # Convert inline code to pure text
    for code in soup.find_all("code"):
        code_text = code.get_text().strip()
        code.replace_with(f" {code_text} ")

    # Strip links: replace <a>link text</a> with JUST "link text" (NO [text](url) markdown!)
    for a in soup.find_all("a"):
        link_text = a.get_text().strip()
        a.replace_with(f" {link_text} " if link_text else "")

    # Convert strong / bold
    for strong in soup.find_all(["strong", "b"]):
        st_text = strong.get_text().strip()
        strong.replace_with(f" {st_text} " if st_text else "")

    # Convert list items
    for li in soup.find_all("li"):
        li_text = li.get_text().strip()
        if li_text:
            li.replace_with(f"\n• {li_text}")

    # Convert paragraphs
    for p in soup.find_all("p"):
        p_text = p.get_text().strip()
        if p_text:
            p.replace_with(f"\n\n{p_text}\n\n")

    text = soup.get_text()
    
    # Clean up boilerplate lines (cookies, subscribe, share, patreon)
    boilerplate = [
        "cookie", "subscribe", "log in", "sign in", "privacy policy", "terms of service",
        "patreon", "skip to content", "all rights reserved", "articles & reviews",
        "news archive", "forums", "premium", "popular categories", "view comments",
        "share this", "leave a comment", "advertisement", "newsletter", "posted on",
        "posted by", "written by", "read more", "comments", "author guide", "events calendar"
    ]

    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        l_str = line.strip()
        if len(l_str) < 15 and not l_str.startswith("•"):
            continue
        if any(b in l_str.lower() for b in boilerplate):
            continue
        # Strip raw URLs if any leaked into text
        l_str = re.sub(r'https?://\S+', '', l_str)
        l_str = re.sub(r'www\.\S+', '', l_str)
        cleaned_lines.append(l_str)

    text = "\n\n".join(cleaned_lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# Alias for backward compatibility
clean_html_to_markdown = clean_html_to_reader_prose

def sanitize_for_speech(text: str) -> str:
    """
    Absolute Firefox/Safari Reading Mode speech sanitizer:
    Strips ALL URLs, http/https characters, slashes, brackets, markdown symbols,
    file extensions, and cleans numbers/abbreviations so voice synthesis sounds 100% natural.
    """
    if not text:
        return ""
    
    t = html.unescape(text)
    
    # 1. Replace markdown link [Label](url) -> Label
    t = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", t)
    
    # 2. Strip all remaining URLs, domains, and protocols
    t = re.sub(r"https?:\/\/\S+", "", t)
    t = re.sub(r"www\.\S+", "", t)
    t = re.sub(r"mailto:\S+", "", t)
    t = re.sub(r"\S+@\S+\.\S+", "", t)
    
    # 3. Strip isolated URL paths & file extensions
    t = re.sub(r"\(\/[^\)]+\)", "", t)
    t = re.sub(r"\/[A-Za-z0-9_\-\.\/]{2,}", "", t)
    t = re.sub(r"\.(php|html|htm|xml|json|rss|atom|asp|aspx|jsp)", "", t, flags=re.IGNORECASE)
    
    # 4. Clean brackets like [1], [2], [$], [#], but keep words
    t = re.sub(r"\[\s*[\d\$#\*\-]+\s*\]", "", t)
    t = re.sub(r"\[\s*\]", "", t)
    
    # 5. Clean version numbers and CVEs
    t = re.sub(r"\bCVE-(\d{4})-(\d+)\b", r"CVE \1 \2", t)
    t = re.sub(r"\bversion\s+v(\d+)", r"version \1", t, flags=re.IGNORECASE)
    t = re.sub(r"\bv(\d+)\.(\d+)\.(\d+)\b", r"version \1 point \2 point \3", t)
    t = re.sub(r"\bv(\d+)\.(\d+)\b", r"version \1 point \2", t)
    
    # 6. Strip symbols, currencies, markdown tags, backticks, slashes
    t = re.sub(r"[`*~_#|<>\/\\\^=+%\$]", " ", t)
    t = re.sub(r"[{}\[\]\(\)]", " ", t)
    t = re.sub(r"—|–|--+", " — ", t)
    
    # 7. Normalize whitespace
    return re.sub(r"\s+", " ", t).strip()
