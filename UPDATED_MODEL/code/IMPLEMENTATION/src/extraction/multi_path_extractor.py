#!/usr/bin/env python3
from pathlib import Path
from typing import List
import hashlib

class RawFact:
    def __init__(self, text, extraction_path, provenance_id):
        self.text = text
        self.extraction_path = extraction_path
        self.provenance_id = provenance_id

class MultiPathExtractor:
    def extract(self, file_path: Path) -> List[RawFact]:
        facts = []
        suffix = file_path.suffix.lower()
        prov = hashlib.md5(str(file_path).encode()).hexdigest()[:8]

        # 1. Plain text fallback
        try:
            txt = Path(file_path).read_text(errors="ignore")
            facts.append(RawFact(txt[:2000], "text", prov))
        except Exception:
            pass

        # 2. PDF text
        if suffix == ".pdf":
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text = "\n".join([p.extract_text() or "" for p in pdf.pages])
                    if text.strip():
                        facts.append(RawFact(text[:2000], "pdf_text", prov))
            except Exception:
                pass
            # OCR fallback for scanned PDFs
            try:
                from pdf2image import convert_from_path
                import pytesseract
                images = convert_from_path(file_path, first_page=1, last_page=1)
                ocr_text = pytesseract.image_to_string(images[0])
                if ocr_text.strip():
                    facts.append(RawFact(ocr_text[:2000], "ocr", prov))
            except Exception:
                pass

        # 3. Excel
        if suffix in [".xlsx", ".xls"]:
            try:
                import pandas as pd
                df = pd.read_excel(file_path, nrows=100)
                facts.append(RawFact(df.to_csv(index=False)[:2000], "excel_table", prov))
            except Exception:
                pass

        # 4. Word
        if suffix == ".docx":
            try:
                from docx import Document
                doc = Document(file_path)
                text = "\n".join([p.text for p in doc.paragraphs])
                facts.append(RawFact(text[:2000], "docx_text", prov))
            except Exception:
                pass

        # 5. PowerPoint
        if suffix == ".pptx":
            try:
                from pptx import Presentation
                prs = Presentation(file_path)
                text = "\n".join([shape.text for s in prs.slides for shape in s.shapes if hasattr(shape,"text")])
                facts.append(RawFact(text[:2000], "pptx_text", prov))
            except Exception:
                pass

        # 6. VLM enrichment placeholder
        try:
            facts.append(RawFact("", "vlm", prov))
        except Exception:
            pass

        return facts
