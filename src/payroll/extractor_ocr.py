from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OcrExtraction:
    text: str
    engine: str


class OcrUnavailableError(RuntimeError):
    pass


def ocr_image(path: Path) -> OcrExtraction:
    """OCR an image file (png/jpg/jpeg) using Tesseract if available.

    Notes:
    - We keep OCR optional in code; if dependencies/binaries are missing, we raise a
      helpful error message that the API can surface.
    - PDF OCR is intentionally not implemented yet (Windows poppler install is noisy).
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
