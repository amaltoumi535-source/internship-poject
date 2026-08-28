"""PDF text extraction for native PDF documents."""

import pdfplumber
from pathlib import Path
from typing import Dict, List, Any

class PDFParser:
    """Extract text from native PDF files (text-based, not scanned)."""

    @staticmethod
    def is_text_pdf(file_path: Path) -> bool:
        """
        Detect if PDF is text-based or scanned.
        Returns True if PDF contains extractable text.
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                # check first up to 3 pages for extractable text
                for page in pdf.pages[:3]:
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:
                        return True
            return False
        except Exception:
            return False

    @staticmethod
    def extract(file_path: Path) -> Dict[str, Any]:
        """
        Extract text from native PDF.

        Returns:
            {
                "text": "full extracted text",
                "metadata": {
                    "total_pages": int,
                    "language": "en/fr",
                    "confidence_score": 0.95
                },
                "pages": [
                    {"page_num": 1, "text": "...", "confidence": 0.98},
                    ...
                ]
            }
        """
        pages_data: List[Dict[str, Any]] = []
        full_text: List[str] = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""

                    pages_data.append({
                        "page_num": page_num,
                        "text": text,
                        "confidence": 0.95  # PDF native text is highly reliable
                    })

                    if text:
                        full_text.append(text)

                return {
                    "text": "\n\n".join(full_text),
                    "metadata": {
                        "total_pages": len(pdf.pages),
                        "language": "multi",  # Could detect with langdetect if needed
                        "confidence_score": 0.95,
                        "parser": "PDFPlumber"
                    },
                    "pages": pages_data
                }

        except Exception as e:
            raise Exception(f"PDF parsing failed: {str(e)}")