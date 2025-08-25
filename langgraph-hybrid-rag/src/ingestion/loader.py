from typing import List
import os
from pypdf import PdfReader
from docx import Document


def load_file_to_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(path)
        return "\n".join([p.extract_text() or "" for p in reader.pages])
    if ext in {".txt", ".md"}:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext == ".docx":
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    raise ValueError(f"Unsupported file type: {ext}")
