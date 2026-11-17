"""Load PDF / DOCX / TXT legal documents into a uniform in-memory form."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("spectre.ingestion")

KNOWN_CATEGORIES = {"acts", "judgements", "regulations", "other"}


class DocumentLoadError(Exception):
    """Raised when a document cannot be read at all."""


@dataclass
class PageText:
    page_number: Optional[int]  # None when the format has no reliable pages (DOCX/TXT)
    text: str


@dataclass
class LoadedDocument:
    doc_id: str
    path: Path
    title: str
    short_name: str
    category: str
    year: Optional[int]
    content_hash: str
    pages: list[PageText]
    warnings: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Discovery & manifest
# --------------------------------------------------------------------------- #
def discover_documents(root: Path, extensions: tuple[str, ...]) -> list[Path]:
    root = Path(root)
    if not root.exists():
        return []
    return sorted(
        p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in extensions
    )


def load_manifest(path: Path) -> dict[str, dict]:
    """Read manifest.json into ``{lowercase filename: entry}``.

    Tolerant of several layouts: a list of entries, ``{"documents": [...]}``, or a
    mapping of filename -> entry. Entry keys understood: file/filename/path, title/name,
    short_name/abbreviation, year, category/type.
    """
    path = Path(path)
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read manifest %s: %s", path, exc)
        return {}

    entries = raw.get("documents", raw) if isinstance(raw, dict) else raw
    result: dict[str, dict] = {}
    if isinstance(entries, dict):
        for key, entry in entries.items():
            if isinstance(entry, dict):
                name = entry.get("file") or entry.get("filename") or entry.get("path") or key
                result[Path(str(name)).name.lower()] = entry
    elif isinstance(entries, list):
        for entry in entries:
            if isinstance(entry, dict):
                name = entry.get("file") or entry.get("filename") or entry.get("path")
                if name:
                    result[Path(str(name)).name.lower()] = entry
    return result


# --------------------------------------------------------------------------- #
# Text extraction
# --------------------------------------------------------------------------- #
def _clean(text: str) -> str:
    text = text.replace("\x00", "").replace("­", "")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)  # re-join hyphenated line breaks
    text = re.sub(r"[ \t ]+", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _read_pdf(path: Path) -> list[PageText]:
    from pypdf import PdfReader

    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            reader.decrypt("")
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            pages.append(PageText(i, _clean(page.extract_text() or "")))
        return pages
    except Exception as exc:  # pypdf raises many different error types
        raise DocumentLoadError(f"Cannot read PDF {path.name}: {exc}") from exc

_MIN_PAGE_CHARS = 30  # fewer characters than this on a page = treat the page as empty
_OCR_WARNED = False


def _pypdf_pages(path: Path) -> Optional[list[PageText]]:
    """First-choice extractor. Returns None if pypdf cannot open the file at all."""
    from pypdf import PdfReader

    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            reader.decrypt("")
        return [PageText(i, _clean(p.extract_text() or "")) for i, p in enumerate(reader.pages, start=1)]
    except Exception as exc:  # pypdf raises many different error types
        logger.warning("pypdf failed on %s: %s", path.name, exc)
        return None


def _ocr_page(page) -> str:
    """OCR one PyMuPDF page. Returns "" if Tesseract/pytesseract/Pillow are not installed."""
    global _OCR_WARNED
    try:
        import io

        import pytesseract
        from PIL import Image

        image = Image.open(io.BytesIO(page.get_pixmap(dpi=200).tobytes("png")))
        return _clean(pytesseract.image_to_string(image, lang="eng"))
    except Exception as exc:
        if not _OCR_WARNED:
            logger.warning("OCR unavailable (%s). Install Tesseract + pytesseract + pillow.", exc)
            _OCR_WARNED = True
        return ""


def _read_pdf(path: Path) -> list[PageText]:
    """pypdf -> PyMuPDF -> OCR, applied per page so mixed text/scanned PDFs work."""
    pages = _pypdf_pages(path)
    weak = [i for i, p in enumerate(pages or []) if len(p.text) < _MIN_PAGE_CHARS]
    if pages is not None and not weak:
        return pages

    try:
        import pymupdf
    except ImportError:
        if pages is None:
            raise DocumentLoadError(f"Cannot read PDF {path.name} (pypdf failed; try: pip install pymupdf)")
        return pages

    try:
        doc = pymupdf.open(str(path))
    except Exception as exc:
        if pages is None:
            raise DocumentLoadError(f"Cannot read PDF {path.name}: {exc}") from exc
        return pages
    try:
        if pages is None:
            pages = [PageText(i + 1, "") for i in range(doc.page_count)]
            weak = list(range(len(pages)))
        for i in weak:
            page = doc[i]
            text = _clean(page.get_text("text") or "")
            if len(text) < _MIN_PAGE_CHARS:
                text = _ocr_page(page) or text
            pages[i] = PageText(i + 1, text)
    finally:
        doc.close()
    return pages

def _read_txt(path: Path) -> list[PageText]:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("latin-1")
    chunks = text.split("\f")
    if len(chunks) > 1:
        return [PageText(i, _clean(c)) for i, c in enumerate(chunks, start=1)]
    return [PageText(None, _clean(text))]


_READERS = {".pdf": _read_pdf,".txt": _read_txt}


# --------------------------------------------------------------------------- #
# Metadata inference
# --------------------------------------------------------------------------- #
def _title_from_filename(stem: str) -> str:
    stem = re.sub(r"^\d{6,}[_\-\s]*", "", stem)  # leading timestamps like 1742307191_
    stem = re.sub(r"[_\-]+", " ", stem)
    stem = re.sub(r"\s+\d+$", "", stem)  # trailing copy numbers like "_0"
    return re.sub(r"\s+", " ", stem).strip() or "Untitled document"


def _category(path: Path, root: Optional[Path], entry: dict) -> str:
    declared = entry.get("category") or entry.get("type")
    if declared:
        return str(declared).lower()
    if root is not None:
        try:
            first = path.relative_to(root).parts[0].lower()
            if first in KNOWN_CATEGORIES:
                return first
        except ValueError:
            pass
    return "other"


def load_document(
    path: Path, root: Optional[Path] = None, manifest_entry: Optional[dict] = None
) -> LoadedDocument:
    path = Path(path)
    reader = _READERS.get(path.suffix.lower())
    if reader is None:
        raise DocumentLoadError(f"Unsupported file type: {path.suffix}")

    entry = manifest_entry or {}
    pages = reader(path)
    warnings: list[str] = []
    total_chars = sum(len(p.text) for p in pages)
    if total_chars < 200:
        warnings.append(
            "Very little text extracted - the file may be a scanned image (OCR is not supported)."
        )

    title = str(entry.get("title") or entry.get("name") or _title_from_filename(path.stem))
    short_name = str(entry.get("short_name") or entry.get("abbreviation") or title)
    year = entry.get("year")
    if year is None:
        m = re.search(r"\b(1[89]\d{2}|20\d{2})\b", title)
        year = int(m.group(1)) if m else None

    rel = path.relative_to(root).as_posix() if root and path.is_relative_to(root) else path.name
    digest = hashlib.sha1(rel.encode("utf-8")).hexdigest()[:8]
    slug = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")[:40]

    return LoadedDocument(
        doc_id=f"{slug}-{digest}",
        path=path,
        title=title,
        short_name=short_name,
        category=_category(path, root, entry),
        year=int(year) if year else None,
        content_hash=hashlib.sha256(path.read_bytes()).hexdigest(),
        pages=pages,
        warnings=warnings,
    )
