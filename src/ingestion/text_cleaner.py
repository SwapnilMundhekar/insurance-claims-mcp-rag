import re
import unicodedata


def normalize_unicode(text: str) -> str:
    """
    Normalizes unicode characters so PDF-extracted text becomes more consistent.
    """
    return unicodedata.normalize("NFKC", text)


def remove_excess_whitespace(text: str) -> str:
    """
    Collapses repeated spaces, tabs, and blank lines.
    """
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fix_broken_hyphenation(text: str) -> str:
    """
    Fixes PDF line-break hyphenation like:
    insur-
    ance

    into:
    insurance
    """
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def normalize_line_breaks(text: str) -> str:
    """
    Keeps paragraph structure but removes noisy single line breaks.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    paragraphs = re.split(r"\n\s*\n", text)
    cleaned_paragraphs = []

    for paragraph in paragraphs:
        lines = [line.strip() for line in paragraph.split("\n") if line.strip()]
        cleaned_paragraph = " ".join(lines)
        if cleaned_paragraph:
            cleaned_paragraphs.append(cleaned_paragraph)

    return "\n\n".join(cleaned_paragraphs)


def clean_page_text(text: str) -> str:
    """
    Applies the full page-level cleaning pipeline.
    """
    if not text:
        return ""

    text = normalize_unicode(text)
    text = fix_broken_hyphenation(text)
    text = normalize_line_breaks(text)
    text = remove_excess_whitespace(text)

    return text
