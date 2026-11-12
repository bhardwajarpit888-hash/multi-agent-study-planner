import os
import re
from typing import Optional


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a syllabus PDF using PyMuPDF (fitz) or PyPDF fallback.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    extracted_pages = []

    # Attempt 1: PyMuPDF
    try:
        import pymupdf  # PyMuPDF
        doc = pymupdf.open(pdf_path)
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text("text")
            if text.strip():
                extracted_pages.append(f"--- Page {page_idx + 1} ---\n{text}")
        doc.close()
        if extracted_pages:
            return clean_extracted_text("\n\n".join(extracted_pages))
    except Exception as e:
        print(f"[PDFParser] PyMuPDF extraction warning: {e}. Trying pypdf...")

    # Attempt 2: PyPDF fallback
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                extracted_pages.append(f"--- Page {idx + 1} ---\n{text}")
        if extracted_pages:
            return clean_extracted_text("\n\n".join(extracted_pages))
    except Exception as e:
        print(f"[PDFParser] pypdf extraction error: {e}")

    raise ValueError("Failed to extract readable text from the syllabus PDF.")


def clean_extracted_text(raw_text: str) -> str:
    """
    Cleans up noisy whitespace, repeated hyphens, and non-printable characters.
    """
    # Replace carriage returns
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple consecutive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse irregular horizontal spaces
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()
