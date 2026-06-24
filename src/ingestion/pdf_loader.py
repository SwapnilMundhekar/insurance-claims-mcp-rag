from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib
import fitz


@dataclass
class ExtractedPage:
    document_id: str
    document_name: str
    page_number: int
    total_pages: int
    text: str
    char_count: int
    extraction_method: str


def build_document_id(pdf_path: Path) -> str:
    """
    Creates a stable document ID from the PDF file name.
    This avoids exposing full local machine paths in the extracted output.
    """
    return hashlib.sha1(pdf_path.name.encode("utf-8")).hexdigest()[:12]


def extract_pages_from_pdf(pdf_path: Path) -> list[dict]:
    """
    Extracts text page by page from a single PDF.

    pdf_path: Path object pointing to one PDF file.
    returns: list of dictionaries, one dictionary per PDF page.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document_id = build_document_id(pdf_path)
    extracted_pages: list[dict] = []

    with fitz.open(pdf_path) as pdf_document:
        total_pages = pdf_document.page_count

        for page_index in range(total_pages):
            page = pdf_document.load_page(page_index)
            text = page.get_text("text").strip()

            page_record = ExtractedPage(
                document_id=document_id,
                document_name=pdf_path.name,
                page_number=page_index + 1,
                total_pages=total_pages,
                text=text,
                char_count=len(text),
                extraction_method="pymupdf_text",
            )

            extracted_pages.append(asdict(page_record))

    return extracted_pages


def extract_pages_from_folder(pdf_source_dir: Path) -> list[dict]:
    """
    Extracts pages from all PDF files inside a folder.

    pdf_source_dir: folder containing policy/regulatory PDFs.
    returns: list of page dictionaries across all PDFs.
    """
    pdf_source_dir = Path(pdf_source_dir)

    if not pdf_source_dir.exists():
        raise FileNotFoundError(f"PDF source folder not found: {pdf_source_dir}")

    pdf_files = sorted(pdf_source_dir.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in: {pdf_source_dir}")

    all_pages: list[dict] = []

    for pdf_file in pdf_files:
        pages = extract_pages_from_pdf(pdf_file)
        all_pages.extend(pages)

    return all_pages
