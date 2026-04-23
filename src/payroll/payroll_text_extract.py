from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.payroll.extractor_ocr import OcrUnavailableError, ocr_image, ocr_pdf_scanned
from src.payroll.extractor_pdf import extract_text_from_pdf


def looks_like_scanned_pdf(*, page_count: int, extracted_text: str) -> bool:
    if page_count <= 0:
        return False
    txt = (extracted_text or "").strip()
    if len(txt) < 50:
        return True
    alpha = sum(1 for c in txt if c.isalpha())
    ratio = alpha / max(1, len(txt))
    return ratio < 0.05


def native_pdf_text_insufficient(text: str, page_count: int) -> bool:
    """True when pdfplumber text is empty, very short, or looks like a scanned artifact."""

    t = (text or "").strip()
    if not t:
        return True
    if len(t) < 60:
        return True
    if looks_like_scanned_pdf(page_count=page_count, extracted_text=t):
        return True
    return False


@dataclass(frozen=True)
class RawPayrollTextResult:
    text: str
    ocr_used: bool
    extraction_source: str  # native_pdf | pdf_ocr_fallback | image_ocr
    pdf_page_count: int | None = None
    native_pdf_chars: int | None = None


def extract_raw_payroll_text(path: Path) -> RawPayrollTextResult:
    """Load raw text from a payroll file: native PDF text, or OCR (image / scanned PDF fallback).

    Raises:
        OcrUnavailableError: Missing OCR/PyMuPDF deps or OCR produced no usable text for PDF fallback.
        FileNotFoundError: Path does not exist.
        ValueError: Unsupported extension.
    """

    if not path.exists():
        raise FileNotFoundError(str(path))

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        pdf_res = extract_text_from_pdf(path)
        native = pdf_res.text or ""
        native_stripped = native.strip()
        native_len = len(native_stripped)

        if not native_pdf_text_insufficient(native_stripped, pdf_res.page_count):
            return RawPayrollTextResult(
                text=native,
                ocr_used=False,
                extraction_source="native_pdf",
                pdf_page_count=pdf_res.page_count,
                native_pdf_chars=native_len,
            )

        ocr_res = ocr_pdf_scanned(path)
        ocr_stripped = (ocr_res.text or "").strip()
        if not ocr_stripped:
            raise OcrUnavailableError(
                "This PDF has little or no selectable text (likely scanned). OCR ran but returned no text. "
                "Check that Tesseract is installed and on PATH, then retry—or upload a PNG/JPG of the paystub."
            )
        return RawPayrollTextResult(
            text=ocr_res.text,
            ocr_used=True,
            extraction_source="pdf_ocr_fallback",
            pdf_page_count=pdf_res.page_count,
            native_pdf_chars=native_len,
        )

    if suffix in {".png", ".jpg", ".jpeg"}:
        ocr_res = ocr_image(path)
        return RawPayrollTextResult(
            text=ocr_res.text,
            ocr_used=True,
            extraction_source="image_ocr",
            pdf_page_count=None,
            native_pdf_chars=None,
        )

    raise ValueError(f"Unsupported payroll file type: {suffix}")
