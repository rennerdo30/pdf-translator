"""OCR processing for scanned PDF pages."""

from typing import Optional

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

import io


class OCRProcessor:
    """Handles OCR for scanned document pages."""
    
    def __init__(self, language: str = "eng"):
        """Initialize OCR processor.
        
        Args:
            language: Tesseract language code (e.g., 'eng', 'deu', 'jpn')
        """
        self.language = self._normalize_language(language)
    
    def _normalize_language(self, language: str) -> str:
        """Convert language name to Tesseract code."""
        lang_map = {
            "english": "eng",
            "german": "deu",
            "french": "fra",
            "spanish": "spa",
            "italian": "ita",
            "portuguese": "por",
            "dutch": "nld",
            "russian": "rus",
            "chinese": "chi_sim",
            "japanese": "jpn",
            "korean": "kor",
            "arabic": "ara",
            "auto": "eng",  # Default to English for auto
        }
        return lang_map.get(language.lower(), language)
    
    def is_available(self) -> bool:
        """Check if Tesseract is available."""
        if not TESSERACT_AVAILABLE:
            return False
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
    
    def extract_text(self, image_bytes: bytes) -> str:
        """Extract text from an image using OCR.
        
        Args:
            image_bytes: PNG image bytes
            
        Returns:
            Extracted text from the image
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError(
                "pytesseract is not installed. "
                "Install it with: pip install pytesseract"
            )
        
        image = Image.open(io.BytesIO(image_bytes))
        
        # Run OCR
        text = pytesseract.image_to_string(
            image,
            lang=self.language,
            config="--psm 1",  # Automatic page segmentation with OSD
        )
        
        return text.strip()
    
    def extract_text_with_positions(
        self,
        image_bytes: bytes
    ) -> list[dict]:
        """Extract text with bounding box positions.
        
        Args:
            image_bytes: PNG image bytes
            
        Returns:
            List of dicts with 'text', 'x', 'y', 'width', 'height'
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("pytesseract is not installed")
        
        image = Image.open(io.BytesIO(image_bytes))
        
        # Get detailed OCR data
        data = pytesseract.image_to_data(
            image,
            lang=self.language,
            output_type=pytesseract.Output.DICT,
        )
        
        results = []
        n_boxes = len(data["text"])
        
        for i in range(n_boxes):
            text = data["text"][i].strip()
            if text:
                results.append({
                    "text": text,
                    "x": data["left"][i],
                    "y": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i],
                    "confidence": data["conf"][i],
                })
        
        return results
