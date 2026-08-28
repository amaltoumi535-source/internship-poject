"""OCR text extraction for scanned documents and images using Tesseract."""

import pytesseract
from PIL import Image
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class OCRParser:
    """
    Extract text from scanned PDFs and images using Tesseract.
    Includes image preprocessing for better OCR accuracy.
    """

    # Language configurations
    LANGUAGES = {
        "fr": "fra",      # French
        "en": "eng",      # English
        "multi": "fra+eng"  # Both
    }

    @staticmethod
    def preprocess_image(image_path: Path) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.

        Steps:
        1. Read image
        2. Convert to grayscale
        3. Denoise (optional)
        4. Adjust contrast
        5. Threshold
        """
        # Read image
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, h=10)

        # Increase contrast (CLAHE - Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # Apply threshold for better text extraction
        _, threshold = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return threshold

    @staticmethod
    def extract(file_path: Path, lang: str = "multi") -> Dict[str, Any]:
        """
        Extract text from image using Tesseract OCR.

        Args:
            file_path: Path to image file
            lang: Language code ("fr", "en", "multi")

        Returns:
            {
                "text": "extracted text",
                "metadata": {
                    "language": "en/fr",
                    "confidence_score": 0.87,
                    "preprocessing_applied": True
                },
                "raw_text": "unprocessed OCR output",
                "confidence": 0.87
            }
        """
        try:
            # Preprocess image
            processed_img = OCRParser.preprocess_image(file_path)

            # Map language code to Tesseract config
            tesseract_lang = OCRParser.LANGUAGES.get(lang, "fra+eng")

            # Extract text with Tesseract
            raw_text = pytesseract.image_to_string(
                processed_img,
                lang=tesseract_lang,
                config="--psm 6"  # PSM 6: Assume a single uniform block of text
            )

            # Get confidence data
            data = pytesseract.image_to_data(
                processed_img,
                lang=tesseract_lang,
                output_type=pytesseract.Output.DICT
            )

            # Calculate average confidence
            confidences = []
            if isinstance(data.get("conf"), (list, tuple)):
                for conf in data["conf"]:
                    try:
                        c = float(conf)
                        if c > 0:
                            confidences.append(c)
                    except Exception:
                        continue
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            confidence_score = avg_confidence / 100.0

            # Clean text
            cleaned_text = OCRParser._clean_text(raw_text)

            return {
                "text": cleaned_text,
                "metadata": {
                    "language": lang,
                    "confidence_score": round(confidence_score, 2),
                    "preprocessing_applied": True,
                    "parser": "Tesseract"
                },
                "raw_text": raw_text,
                "confidence": confidence_score
            }

        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise Exception(f"OCR extraction failed: {str(e)}")

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean OCR output.
        - Remove extra whitespace
        - Remove very short isolated lines
        """
        # Remove multiple spaces/newlines and very short lines
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line and len(line) > 2]

        cleaned = '\n'.join(lines)
        return cleaned