from dataclasses import asdict, dataclass
from hashlib import sha1
import re
from typing import Any

from src.chunking.section_detector import (
    estimate_token_count,
    infer_chunk_type,
    is_probable_heading,
    split_into_paragraphs,
)


@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    document_name: str
    document_type: str
    provider_or_regulator: str
    product_type: str
    jurisdiction: str
    source_category: str
    section_title: str
    chunk_type: str
    start_page: int
    end_page: int
    source_references: list[str]
    text: str
    char_count: int
    estimated_tokens: int


def build_chunk_id(document_id: str, start_page: int, chunk_index: int, text: str) -> str:
    """
    Creates a stable chunk ID using document ID, page, index, and text hash.
    """
    raw_value = f"{document_id}:{start_page}:{chunk_index}:{text[:120]}"
    return sha1(raw_value.encode("utf-8")).hexdigest()[:16]


def split_long_paragraph(paragraph: str, max_tokens: int) -> list[str]:
    """
    Splits very long paragraphs into sentence groups.

    This is only used when a single paragraph is too large.
    """
    if estimate_token_count(paragraph) <= max_tokens:
        return [paragraph]

    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    groups: list[str] = []
    current_group: list[str] = []

    for sentence in sentences:
        candidate = " ".join(current_group + [sentence]).strip()

        if current_group and estimate_token_count(candidate) > max_tokens:
            groups.append(" ".join(current_group).strip())
            current_group = [sentence]
        else:
            current_group.append(sentence)

    if current_group:
        groups.append(" ".join(current_group).strip())

    return [group for group in groups if group]


def flatten_pages_into_units(clean_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts cleaned page records into paragraph-level semantic units.
    """
    units: list[dict[str, Any]] = []
    current_section_title = "Document Introduction"

    for page in clean_pages:
        paragraphs = split_into_paragraphs(page.get("clean_text", ""))

        for paragraph in paragraphs:
            if is_probable_heading(paragraph):
                current_section_title = paragraph
                continue

            units.append(
                {
                    "document_id": page["document_id"],
                    "document_name": page["document_name"],
                    "document_type": page["document_type"],
                    "provider_or_regulator": page["provider_or_regulator"],
                    "product_type": page["product_type"],
                    "jurisdiction": page["jurisdiction"],
                    "source_category": page["source_category"],
                    "section_title": current_section_title,
                    "page_number": page["page_number"],
                    "source_reference": page["source_reference"],
                    "text": paragraph,
                }
            )

    return units


def emit_chunk(
    buffer: list[dict[str, Any]],
    chunk_index: int,
) -> dict[str, Any]:
    """
    Converts a buffer of paragraph units into one metadata-rich chunk.
    """
    first = buffer[0]
    section_title = first["section_title"]

    text_parts = []

    if section_title:
        text_parts.append(f"Section: {section_title}")

    text_parts.extend(unit["text"] for unit in buffer)

    chunk_text = "\n\n".join(text_parts).strip()

    pages = [unit["page_number"] for unit in buffer]
    source_references = sorted(set(unit["source_reference"] for unit in buffer))

    chunk = DocumentChunk(
        chunk_id=build_chunk_id(
            document_id=first["document_id"],
            start_page=min(pages),
            chunk_index=chunk_index,
            text=chunk_text,
        ),
        document_id=first["document_id"],
        document_name=first["document_name"],
        document_type=first["document_type"],
        provider_or_regulator=first["provider_or_regulator"],
        product_type=first["product_type"],
        jurisdiction=first["jurisdiction"],
        source_category=first["source_category"],
        section_title=section_title,
        chunk_type=infer_chunk_type(section_title, chunk_text),
        start_page=min(pages),
        end_page=max(pages),
        source_references=source_references,
        text=chunk_text,
        char_count=len(chunk_text),
        estimated_tokens=estimate_token_count(chunk_text),
    )

    return asdict(chunk)


def build_chunks_for_document(
    clean_pages: list[dict[str, Any]],
    min_tokens: int = 120,
    max_tokens: int = 650,
    overlap_units: int = 1,
) -> list[dict[str, Any]]:
    """
    Builds section-aware chunks for one document.

    The algorithm keeps paragraphs from the same section together where possible.
    """
    units = flatten_pages_into_units(clean_pages)

    expanded_units: list[dict[str, Any]] = []

    for unit in units:
        split_texts = split_long_paragraph(unit["text"], max_tokens=max_tokens)

        for split_text in split_texts:
            new_unit = dict(unit)
            new_unit["text"] = split_text
            expanded_units.append(new_unit)

    chunks: list[dict[str, Any]] = []
    buffer: list[dict[str, Any]] = []
    chunk_index = 1

    for unit in expanded_units:
        candidate_buffer = buffer + [unit]
        candidate_text = "\n\n".join(item["text"] for item in candidate_buffer)
        candidate_tokens = estimate_token_count(candidate_text)

        section_changed = bool(buffer and unit["section_title"] != buffer[-1]["section_title"])

        should_emit = False

        if buffer and section_changed and estimate_token_count(candidate_text) >= min_tokens:
            should_emit = True

        if buffer and candidate_tokens > max_tokens:
            should_emit = True

        if should_emit:
            chunks.append(emit_chunk(buffer, chunk_index))
            chunk_index += 1

            if overlap_units > 0:
                buffer = buffer[-overlap_units:]
            else:
                buffer = []

        buffer.append(unit)

    if buffer:
        chunks.append(emit_chunk(buffer, chunk_index))

    return chunks


def build_chunks(
    clean_pages: list[dict[str, Any]],
    min_tokens: int = 120,
    max_tokens: int = 650,
    overlap_units: int = 1,
) -> list[dict[str, Any]]:
    """
    Builds chunks across all documents.
    """
    pages_by_document: dict[str, list[dict[str, Any]]] = {}

    for page in clean_pages:
        pages_by_document.setdefault(page["document_name"], []).append(page)

    all_chunks: list[dict[str, Any]] = []

    for document_name, document_pages in sorted(pages_by_document.items()):
        sorted_pages = sorted(document_pages, key=lambda item: item["page_number"])

        document_chunks = build_chunks_for_document(
            clean_pages=sorted_pages,
            min_tokens=min_tokens,
            max_tokens=max_tokens,
            overlap_units=overlap_units,
        )

        all_chunks.extend(document_chunks)

    return all_chunks
