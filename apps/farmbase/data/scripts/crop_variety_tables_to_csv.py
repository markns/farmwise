#!/usr/bin/env python3
"""
Extract crop‑variety tables from the per‑crop PDFs produced from the
*Kenyan National Crop Variety List – 2025 edition* and merge them into
one CSV.

Key features
------------
• Accepts a directory of split PDFs (one crop per file).
• Fixes wrapped header words (e.g. “Duratio n” → “Duration”).
• Detects and merges multi‑page rows (data that spills onto the next
  page is appended to the previous row).
• Adds a 'Crop' column derived from each PDF’s filename.
• Pure‑Python: only needs pdfplumber and pandas.

Usage
-----
    pip install pdfplumber pandas
    python extract_crop_tables_to_csv.py \
           --pdf-dir crop_variety_splits_by_header \
           --out     national_crop_varieties_2025.csv
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
import pdfplumber


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def fix_header_words(raw: str) -> str:
    """Join words split across a space by the PDF line‑breaking."""
    cleaned = re.sub(r"\s+", " ", raw).strip()

    tokens = cleaned.split(" ")
    fixed: list[str] = []
    skip_next = False
    for i, tok in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue

        # if the following token is a single letter, join them
        if i < len(tokens) - 1 and len(tokens[i + 1]) == 1:
            fixed.append(tok + tokens[i + 1])
            skip_next = True
        elif len(tok) == 1 and fixed:
            # stray single letter belongs to previous token
            fixed[-1] += tok
        else:
            fixed.append(tok)
    return " ".join(fixed)


def looks_like_header(row: list[str], header: list[str]) -> bool:
    """Return True if *row* matches the header (≥ ½ of the columns equal)."""
    cmp_row = [fix_header_words(c or "").strip().lower() for c in row]
    cmp_hdr = [h.strip().lower() for h in header]

    matches = sum(1 for a, b in zip(cmp_row, cmp_hdr) if a and b and a == b)
    return matches >= len(header) // 2


def merge_broken_rows(rows: list[list[str]], ncols: int) -> list[list[str]]:
    """Merge rows whose first cell is empty into the previous row."""
    merged: list[list[str]] = []
    for row in rows:
        row = [(cell or "").strip() for cell in row]
        # normalise width
        if len(row) < ncols:
            row += [""] * (ncols - len(row))
        elif len(row) > ncols:
            row = row[:ncols]

        if merged and (row[0] == "" or all(c == "" for c in row[:1])):
            # continuation: append cell‑wise
            prev = merged[-1]
            merged[-1] = [(prev[i] + "\n" + row[i]) if row[i] else prev[i] for i in range(ncols)]
        else:
            merged.append(row)
    return merged


def extract_table(pdf_path: Path) -> pd.DataFrame:
    crop = pdf_path.stem.split("_", 1)[-1]  # e.g. '03_TEA' → 'TEA'
    header: list[str] | None = None
    data_rows: list[list[str]] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page = page.within_bbox(page.cropbox)
            tbl = page.extract_table()
            if not tbl:
                continue

            # First row encountered is assumed to be the header
            if header is None:
                header = [fix_header_words(col or "") for col in tbl[0]]
                candidate_rows = tbl[1:]
            else:
                candidate_rows = tbl

            # Skip rows that are just repeated headers
            for row in candidate_rows:
                if looks_like_header(row, header):
                    continue
                data_rows.append(row)

    if header is None:
        raise ValueError(f"No table found in {pdf_path}")

    cleaned_rows = merge_broken_rows(data_rows, len(header))

    print(cleaned_rows)
    print(header)
    df = pd.DataFrame(cleaned_rows, columns=header)
    df.insert(0, "Crop", crop)
    return df


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description="Parse crop tables into CSV")
    ap.add_argument(
        "--pdf-dir",
        type=Path,
        # required=True,
        default=Path("crop_variety_splits_by_header"),
        help="Directory containing the per‑crop PDF files",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("crop_variety_splits_by_header_df"),
        help="Output CSV filename",
    )
    args = ap.parse_args()

    pdf_files = sorted(args.pdf_dir.glob("*.pdf"))
    if not pdf_files:
        ap.error("No PDF files found in the specified directory.")

    for pdf in pdf_files:
        print(f"→ Parsing {pdf.name} ...", flush=True)
        df = extract_table(pdf)
        df.to_csv(args.out.joinpath(pdf.name.replace("pdf", "csv")), index=False)

    # full = pd.concat(frames, ignore_index=True)
    # print(f"✅ Saved {len(full)} rows to {args.out}")


if __name__ == "__main__":
    main()
