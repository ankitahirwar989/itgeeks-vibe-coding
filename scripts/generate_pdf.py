"""Generate corpus/academic_regulations.pdf from a plain-text source using PyMuPDF.

Run once during corpus authoring:  python scripts/generate_pdf.py
"""
import pymupdf as fitz
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "corpus" / "_academic_regulations_source.txt"
OUTPUT = Path(__file__).resolve().parent.parent / "corpus" / "academic_regulations.pdf"

PAGE_WIDTH, PAGE_HEIGHT = 595, 842  # A4 in points
MARGIN = 56
FONT = "helv"
BODY_SIZE = 10.5
LINE_HEIGHT = 14.5


def is_heading_line(line: str) -> bool:
    if not line:
        return False
    if line.isupper():
        return True
    first_token = line.split(" ")[0]
    return bool(first_token) and first_token[0].isdigit() and "." in first_token and len(line) < 90


def wrap_paragraph(paragraph: str, max_chars: int = 92) -> list[str]:
    words = paragraph.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = f"{cur} {w}".strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def wrap_text(text: str, max_chars: int = 92):
    """Return list of (line, is_heading) pairs.

    The source is hand-wrapped at ~72 chars, so a single logical "record" (one heading plus
    its body paragraph) spans several raw lines with no blank line in between; only a blank
    line separates one record from the next. We therefore split on blank lines first, treat
    only the FIRST raw line of each resulting block as a heading candidate, and join the
    remaining raw lines into one logical paragraph before re-wrapping — this way a body
    sentence that happens to contain "Section\\n14.2 of the..." can never be mistaken for a
    heading just because hand-wrapping put it at the start of a raw line.
    """
    lines: list[tuple[str, bool]] = []
    blocks = text.split("\n\n")
    for block_index, block in enumerate(blocks):
        raw_lines = [ln for ln in block.split("\n")]
        raw_lines = [ln for ln in raw_lines if ln.strip()] if not raw_lines[0].strip() else raw_lines
        if not raw_lines:
            continue
        first, rest = raw_lines[0].strip(), raw_lines[1:]
        heading = is_heading_line(first)
        for w_line in wrap_paragraph(first, max_chars):
            lines.append((w_line, heading))
        if rest:
            body_paragraph = " ".join(ln.strip() for ln in rest if ln.strip())
            for w_line in wrap_paragraph(body_paragraph, max_chars):
                lines.append((w_line, False))
        if block_index != len(blocks) - 1:
            lines.append(("", False))
    return lines


def main():
    raw = SOURCE.read_text(encoding="utf-8")
    pages = [p.strip("\n") for p in raw.split("===PAGE===") if p.strip()]

    doc = fitz.open()
    for page_text in pages:
        page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        y = MARGIN
        for line, is_heading in wrap_text(page_text.strip()):
            if y > PAGE_HEIGHT - MARGIN:
                page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
                y = MARGIN
            size = BODY_SIZE + 1.5 if is_heading else BODY_SIZE
            page.insert_text((MARGIN, y), line, fontname=FONT, fontsize=size)
            y += LINE_HEIGHT if not is_heading else LINE_HEIGHT + 4

    doc.save(OUTPUT)
    doc.close()
    print(f"Wrote {OUTPUT} with {len(pages)} logical pages")


if __name__ == "__main__":
    main()
