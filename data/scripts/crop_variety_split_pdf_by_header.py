# \"\"\"
# Enhanced splitter for the Kenyan NATIONAL CROP VARIETY LIST (2025).
#
# Key differences from the first version:
# • Splits *inside* pages – no data from the previous crop bleeds into the next.
#   The cut is made exactly at each “NATIONAL … VARIETY LIST” header.
# • Top‑of‑page fragments that precede a header are retained in the previous
#   crop’s PDF; the portion from the header downward starts the new PDF.
#
# Requires: pip install pymupdf  (import fitz)
#
# Run:
#     python split_crop_variety_pdf_by_header.py \
#            "NATIONAL CROP VARIETY LIST 2025 EDITION.pdf"
#
# Outputs one PDF per crop in ./crop_variety_splits_by_header/
# and bundles them into crop_variety_splits_by_header.zip
# \"\"\"

from __future__ import annotations

import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

# HEADER_RE = re.compile(r"(\\d+)\\.\\s*NATIONAL\\s+([A-Z ]+?)\\s+VARIETY LIST", re.I)
HEADER_RE = re.compile(r"^\s*(\d+)\.\s+NATIONAL\s+([A-Z][A-Za-z &]+?)\s+VARIETY\s+LIST", re.MULTILINE)
FIRST_CONTENT_PAGE = 4  # zero‑indexed: skip front‑matter before page 5


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")


class Anchor:
    # \"\"\"A header’s position in the document.\"\"\"

    def __init__(self, page: int, y: float, number: int, crop: str):
        self.page = page
        self.y = y
        self.number = number
        self.crop = crop

    def __repr__(self) -> str:  # for debug
        return f"Anchor(page={self.page}, y={self.y:.1f}, {self.number}. {self.crop})"


def find_anchors(doc: fitz.Document) -> list["Anchor"]:
    anchors = []
    for page_index in range(FIRST_CONTENT_PAGE, len(doc)):
        text = doc[page_index].get_text("text")
        for m in HEADER_RE.finditer(text):
            header_text = m.group(0).strip()
            rects = doc[page_index].search_for(header_text, flags=1)  # 1 = ignore‑case
            if not rects:
                continue
            y_top = rects[0].y0
            anchors.append(
                Anchor(
                    page=page_index,
                    y=y_top,
                    number=int(m.group(1)),
                    crop=m.group(2).strip(),
                )
            )
    anchors.sort(key=lambda a: (a.page, a.y))
    return anchors


def export_region(
    src: fitz.Document,
    start_page: int,
    start_y: float,
    end_page: int,
    end_y: float | None,
) -> fitz.Document:
    # \"\"\"Return a new PDF containing the rectangular slice between two anchor points.\"\"\"
    out = fitz.open()
    for p in range(start_page, end_page + 1):
        out.insert_pdf(src, from_page=p, to_page=p)
    for local_idx, p in enumerate(range(start_page, end_page + 1)):
        page = out[local_idx]
        rect = page.rect
        top = start_y if p == start_page else 0
        bottom = end_y if (end_y is not None and p == end_page) else rect.y1

        clip = fitz.Rect(0, top, rect.x1, bottom)
        page.set_cropbox(clip)

    return out


def split_at_anchors(src_pdf: Path, out_dir: Path) -> list[Path]:
    doc = fitz.open(src_pdf)
    anchors = find_anchors(doc)
    if not anchors:
        raise RuntimeError("No headers detected – aborting.")

    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []

    for idx, anchor in enumerate(anchors):
        next_anchor = anchors[idx + 1] if idx + 1 < len(anchors) else None
        print(anchor.crop)
        out_pdf = export_region(
            src=doc,
            start_page=anchor.page,
            start_y=anchor.y,
            end_page=next_anchor.page if next_anchor else len(doc) - 1,
            end_y=next_anchor.y if next_anchor else None,
        )
        filename = f"{anchor.number:02d}_{slug(anchor.crop)}.pdf"
        out_path = out_dir / filename
        out_pdf.save(out_path)
        outputs.append(out_path)

    return outputs


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("../kalro/NATIONAL CROP VARIETY LIST 2025 EDITION.pdf")
    if not src.exists():
        sys.exit(f"✗ Source PDF not found: {src}")

    out_dir = Path("crop_variety_splits_by_header")
    created = split_at_anchors(src, out_dir)

    print(f"✅ Split {len(created)} crops. PDFs in {out_dir}")


if __name__ == "__main__":
    main()
