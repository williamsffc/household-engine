from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OcrExtraction:
    text: str
    engine: str


class OcrUnavailableError(RuntimeError):
    pass


def ocr_pdf_scanned(path: Path, *, max_pages: int = 4, zoom: float = 2.0) -> OcrExtraction:
    """Rasterize PDF pages with PyMuPDF and OCR each page with Tesseract.

    Used only as a fallback when native PDF text is missing or insufficient (Step 24).
    Does not require Poppler on Windows (unlike pdf2image).
    """

    if path.suffix.lower() != ".pdf":
        raise ValueError("ocr_pdf_scanned expects a .pdf file")

    try:
        import fitz  # PyMuPDF  # type: ignore
    except Exception as e:  # pragma: no cover
        raise OcrUnavailableError(
            "Scanned PDF OCR needs PyMuPDF. Install with: pip install pymupdf"
        ) from e

    try:
        from PIL import Image  # type: ignore
        import pytesseract  # type: ignore
    except Exception as e:  # pragma: no cover
        raise OcrUnavailableError(
            "OCR dependencies not installed. Install Pillow + pytesseract, and ensure the "
            "Tesseract binary is installed and on PATH."
        ) from e

    if not path.exists():
        raise FileNotFoundError(str(path))

    chunks: list[str] = []
    doc = fitz.open(str(path))
    try:
        n = min(len(doc), max(1, int(max_pages)))
        mat = fitz.Matrix(float(zoom), float(zoom))
        for i in range(n):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            chunks.append((pytesseract.image_to_string(img) or "").strip())
    finally:
        doc.close()

    text = "\n\n".join(c for c in chunks if c).strip()
    return OcrExtraction(text=text, engine="tesseract+pymupdf")


def ocr_image(path: Path) -> OcrExtraction:
    """OCR an image file (png/jpg/jpeg) using Tesseract if available.

    Notes:
    - We keep OCR optional in code; if dependencies/binaries are missing, we raise a
      helpful error message that the API can surface.
    - Scanned PDFs use `ocr_pdf_scanned` (PyMuPDF + Tesseract), not this entrypoint.
    """

    suffix = path.suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg"}:
        raise ValueError("ocr_image expects a .png/.jpg/.jpeg file")

    try:
        from PIL import Image  # type: ignore
        import pytesseract  # type: ignore
    except Exception as e:  # pragma: no cover
        raise OcrUnavailableError(
            "OCR dependencies not installed. Install Pillow + pytesseract, and ensure the "
            "Tesseract binary is installed and on PATH."
        ) from e

    if not path.exists():
        raise FileNotFoundError(str(path))

    img = Image.open(str(path))
    text = (pytesseract.image_to_string(img) or "").strip()
    return OcrExtraction(text=text, engine="tesseract")
