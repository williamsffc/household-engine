from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pdfplumber


@dataclass(frozen=True)
class PdfTextExtraction:
    text: str
    page_count: int


def extract_text_from_pdf(path: Path) -> PdfTextExtraction:
    """Extract native (selectable) text from a PDF.

    This intentionally does *not* do OCR; scanned PDFs will usually yield empty text.
    """

    if not path.exists():
        raise FileNotFoundError(str(path))
    if path.suffix.lower() != ".pdf":
        raise ValueError("extract_text_from_pdf expects a .pdf file")

    chunks: list[str] = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            page_text = (page.extract_text() or "").strip()
            if page_text:
                chunks.append(page_text)

        page_count = len(pdf.pages)

    text = "\n\n".join(chunks).strip()
    return PdfTextExtraction(text=text, page_count=page_count)
