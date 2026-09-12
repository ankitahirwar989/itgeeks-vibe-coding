"""Document parsers: turn a corpus file into a list of citable section chunks.

Every chunk maps to exactly one numbered section (e.g. "3.1") in exactly one
source document, so it can be cited as ``<filename>#<section_id>``. This is
the unit the retriever fetches and the unit the reasoning engine quotes from.
"""
import re
from dataclasses import dataclass
from pathlib import Path

import pymupdf as fitz

_MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(?:(\d+(?:\.\d+)*)\.?\s+)?(.+?)\s*$")
_SECTION_LINE_RE = re.compile(r"^(\d+\.\d+)\s+(.+?)\s*$")
_TOP_LEVEL_LINE_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z \-/&,]+)\s*$")


@dataclass
class SectionChunk:
    source_file: str
    section_id: str
    heading: str
    text: str
    page: int | None = None

    @property
    def citation(self) -> str:
        if self.page is not None:
            return f"{self.source_file}#{self.section_id}"
        return f"{self.source_file}#{self.section_id}"


def parse_markdown(path: Path) -> list[SectionChunk]:
    source_file = path.name
    lines = path.read_text(encoding="utf-8").splitlines()

    chunks: list[SectionChunk] = []
    current_id: str | None = None
    current_heading = ""
    buffer: list[str] = []

    def flush():
        if current_id is not None:
            text = "\n".join(buffer).strip()
            chunks.append(
                SectionChunk(
                    source_file=source_file,
                    section_id=current_id,
                    heading=current_heading,
                    text=f"{current_heading}\n{text}".strip() if text else current_heading,
                )
            )

    for line in lines:
        m = _MD_HEADING_RE.match(line)
        if m and m.group(2):
            flush()
            current_id = m.group(2)
            current_heading = f"{m.group(2)} {m.group(3)}".strip()
            buffer = []
        elif m and not m.group(2):
            # Non-numbered heading (document title, decorative section titles) - ignored as a
            # chunk boundary but also not accumulated into any section's body.
            continue
        else:
            if line.strip() == "---":
                continue
            buffer.append(line)

    flush()
    return [c for c in chunks if c.text.strip()]


def parse_pdf(path: Path) -> list[SectionChunk]:
    source_file = path.name
    doc = fitz.open(path)

    chunks: list[SectionChunk] = []
    current_id: str | None = None
    current_heading = ""
    current_page: int | None = None
    buffer: list[str] = []

    def flush():
        if current_id is not None:
            text = "\n".join(buffer).strip()
            chunks.append(
                SectionChunk(
                    source_file=source_file,
                    section_id=current_id,
                    heading=current_heading,
                    text=f"{current_heading}\n{text}".strip() if text else current_heading,
                    page=current_page,
                )
            )

    _HEADING_SIZE_THRESHOLD = 11.5

    for page_index in range(doc.page_count):
        page_number = page_index + 1
        page_dict = doc[page_index].get_text("dict")
        text_lines: list[tuple[str, float]] = []
        for block in page_dict.get("blocks", []):
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = "".join(s["text"] for s in spans).strip()
                max_size = max(s["size"] for s in spans)
                text_lines.append((text, max_size))

        for line, size in text_lines:
            if not line:
                buffer.append("")
                continue
            is_large = size > _HEADING_SIZE_THRESHOLD
            sec_m = _SECTION_LINE_RE.match(line) if is_large else None
            top_m = _TOP_LEVEL_LINE_RE.match(line) if is_large else None
            if sec_m:
                flush()
                current_id = sec_m.group(1)
                current_heading = f"{sec_m.group(1)} {sec_m.group(2)}".strip()
                current_page = page_number
                buffer = []
            elif top_m:
                # Chapter-level title line (e.g. "8. EXAMINATION ELIGIBILITY AND ABSENCE").
                # Not itself a citable leaf section; skip as a boundary.
                continue
            else:
                buffer.append(line)

    flush()
    doc.close()
    return [c for c in chunks if c.text.strip()]


def parse_document(path: Path) -> list[SectionChunk]:
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        return parse_markdown(path)
    if suffix == ".pdf":
        return parse_pdf(path)
    raise ValueError(f"Unsupported document type: {path}")


def parse_corpus(corpus_dir: Path) -> list[SectionChunk]:
    """Parse every supported document in the corpus directory (skips private/meta files)."""
    all_chunks: list[SectionChunk] = []
    for path in sorted(corpus_dir.iterdir()):
        if path.name.startswith("_") or path.name == "contradictions.md":
            continue
        if path.suffix.lower() not in {".md", ".markdown", ".pdf"}:
            continue
        all_chunks.extend(parse_document(path))
    return all_chunks
