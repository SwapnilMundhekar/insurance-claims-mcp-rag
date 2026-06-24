import re


HEADING_KEYWORDS = [
    "cover",
    "covered",
    "not covered",
    "exclusion",
    "exclusions",
    "definition",
    "definitions",
    "claim",
    "claims",
    "complaint",
    "complaints",
    "dispute",
    "obligation",
    "obligations",
    "excess",
    "premium",
    "benefit",
    "limits",
    "conditions",
    "responsibilities",
    "evidence",
    "documents",
    "timeframes",
    "operational risk",
    "service provider",
    "material service provider",
]


def estimate_token_count(text: str) -> int:
    """
    Estimates token count without using model-specific tokenization.

    This is only a size guardrail for chunks.
    It is not the main chunking strategy.
    """
    if not text:
        return 0

    word_count = len(re.findall(r"\b\w+\b", text))
    return max(1, int(word_count * 1.3))


def split_into_paragraphs(text: str) -> list[str]:
    """
    Splits cleaned page text into paragraph-like semantic units.
    """
    if not text:
        return []

    paragraphs = re.split(r"\n\s*\n", text)
    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]


def is_probable_heading(text: str) -> bool:
    """
    Detects likely headings from PDF-extracted text.

    This is heuristic-based because insurance PDFs do not always expose clean structure.
    """
    if not text:
        return False

    candidate = text.strip()
    lower_candidate = candidate.lower()

    if len(candidate) > 140:
        return False

    if candidate.endswith(".") and len(candidate.split()) > 6:
        return False

    if re.match(r"^\d+(\.\d+)*\s+[A-Z]", candidate):
        return True

    if re.match(r"^[A-Z][A-Z\s,\-/&()]{4,}$", candidate):
        return True

    if any(keyword in lower_candidate for keyword in HEADING_KEYWORDS):
        if len(candidate.split()) <= 12:
            return True

    if candidate.istitle() and len(candidate.split()) <= 10:
        return True

    return False


def infer_chunk_type(section_title: str, text: str) -> str:
    """
    Infers a rough chunk type for retrieval filtering and later evaluation.
    """
    combined = f"{section_title} {text}".lower()

    if "not covered" in combined or "exclusion" in combined or "excluded" in combined:
        return "exclusion"

    if "definition" in combined or "means" in combined:
        return "definition"

    if "complaint" in combined or "dispute" in combined or "idr" in combined:
        return "complaint_obligation"

    if "claim" in combined or "evidence" in combined or "documents" in combined:
        return "claims_requirement"

    if "cover" in combined or "covered" in combined or "benefit" in combined:
        return "coverage_clause"

    if "operational risk" in combined or "service provider" in combined:
        return "enterprise_risk_control"

    return "general"
