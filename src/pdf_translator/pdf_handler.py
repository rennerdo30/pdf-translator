"""PDF handling - extraction and reconstruction using PyMuPDF."""

import io
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

import fitz  # PyMuPDF

from pdf_translator.config import Config

logger = logging.getLogger("pdf_translator.pdf_handler")


@dataclass
class TextBlock:
    """Represents a block of text with position information."""
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    page_num: int
    font_size: float = 11.0


@dataclass
class PageData:
    """Data for a single PDF page."""
    page_num: int
    width: float
    height: float
    text_blocks: list[TextBlock]
    has_text: bool
    image_bytes: Optional[bytes] = None


class PDFHandler:
    """Handles PDF text extraction and reconstruction."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def extract_pages(self, pdf_path: Path) -> Iterator[PageData]:
        """Extract text and data from each page of the PDF."""
        doc = fitz.open(pdf_path)
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_blocks = self._extract_text_blocks(page, page_num)
                
                # Check if page has meaningful text
                total_text = "".join(block.text for block in text_blocks)
                has_text = len(total_text.strip()) >= self.config.ocr_threshold
                
                # Get page image for vision model or OCR
                image_bytes = None
                if not has_text or self.config.use_vision:
                    image_bytes = self._page_to_image(page)
                
                yield PageData(
                    page_num=page_num,
                    width=page.rect.width,
                    height=page.rect.height,
                    text_blocks=text_blocks,
                    has_text=has_text,
                    image_bytes=image_bytes,
                )
        finally:
            doc.close()
    
    def _extract_text_blocks(self, page: fitz.Page, page_num: int) -> list[TextBlock]:
        """Extract text blocks with positions from a page."""
        blocks = []
        
        # Get text blocks with position info
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        
        for block in text_dict.get("blocks", []):
            if block.get("type") != 0:  # Skip non-text blocks
                continue
            
            block_text = ""
            font_size = 11.0
            
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    block_text += span.get("text", "")
                    font_size = span.get("size", 11.0)
                block_text += "\n"
            
            if block_text.strip():
                blocks.append(TextBlock(
                    text=block_text.strip(),
                    x0=block["bbox"][0],
                    y0=block["bbox"][1],
                    x1=block["bbox"][2],
                    y1=block["bbox"][3],
                    page_num=page_num,
                    font_size=font_size,
                ))
        
        return blocks
    
    def _page_to_image(self, page: fitz.Page, dpi: int = 150) -> bytes:
        """Convert a PDF page to PNG image bytes."""
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        return pix.tobytes("png")
    
    def create_translated_pdf(
        self,
        source_path: Path,
        output_path: Path,
        translated_pages: list[tuple[int, str]],
    ) -> None:
        """Create a new PDF with translated content.
        
        Creates a side-by-side document with original + translation.
        For each page: original page preserved, then translation page added.
        
        Args:
            source_path: Path to the source PDF
            output_path: Path for the output PDF
            translated_pages: List of (page_num, translated_text) tuples
        """
        source_doc = fitz.open(source_path)
        output_doc = fitz.open()  # New empty document
        
        try:
            # Create translation mapping
            translations = {page_num: text for page_num, text in translated_pages}
            
            for page_num in range(len(source_doc)):
                source_page = source_doc[page_num]
                
                # Copy original page to output
                output_doc.insert_pdf(source_doc, from_page=page_num, to_page=page_num)
                
                # If we have a translation, add translation page after original
                if page_num in translations and translations[page_num].strip():
                    translated_text = translations[page_num]
                    self._add_translation_page(
                        output_doc, 
                        translated_text,
                        source_page.rect.width,
                        source_page.rect.height,
                        page_num + 1,  # Original page number for reference
                    )
            
            output_doc.save(output_path)
        finally:
            source_doc.close()
            output_doc.close()
    
    def _add_translation_page(
        self, 
        doc: fitz.Document, 
        translated_text: str,
        width: float,
        height: float,
        original_page_num: int,
    ) -> None:
        """Add a new page with translated text.
        
        Creates a clean, readable translation page that matches source dimensions.
        Uses proportional sizing based on page dimensions.
        """
        # Create new page with same dimensions
        page = doc.new_page(width=width, height=height)
        
        # Calculate scale factor based on page size (reference: 600pt standard)
        scale = min(width, height) / 600.0
        scale = max(0.5, min(scale, 3.0))  # Clamp between 0.5x and 3x
        
        # Proportional sizing
        header_fontsize = 10 * scale
        margin = int(40 * scale)
        
        # Add header with page reference
        header_text = f"Translation of Page {original_page_num}"
        header_x = max(margin, (width - len(header_text) * 5 * scale) / 2)
        page.insert_text(
            fitz.Point(header_x, 25 * scale),
            header_text,
            fontsize=header_fontsize,
            color=(0.4, 0.4, 0.4),
        )
        
        # Draw header line
        line_y = 35 * scale
        page.draw_line(
            fitz.Point(margin, line_y),
            fitz.Point(width - margin, line_y),
            color=(0.8, 0.8, 0.8),
            width=0.5 * scale,
        )
        
        # Text area with proportional margins
        text_rect = fitz.Rect(
            margin,
            45 * scale,
            width - margin,
            height - margin,
        )
        
        # Calculate font size based on page size and text length
        base_fontsize = 12 * scale
        text_length = len(translated_text)
        
        if text_length > 2000:
            fontsize = base_fontsize * 0.75
        elif text_length > 1000:
            fontsize = base_fontsize * 0.85
        else:
            fontsize = base_fontsize
        
        fontsize = max(8, min(fontsize, 48))  # Clamp between 8 and 48
        
        logger.debug(f"Translation page: scale={scale:.2f}, fontsize={fontsize:.1f}")
        
        # Insert text - using insert_textbox for compatibility
        page.insert_textbox(
            text_rect,
            translated_text,
            fontsize=fontsize,
            fontname="helv",
            align=fitz.TEXT_ALIGN_LEFT,
        )
    
    def create_overlay_pdf(
        self,
        source_path: Path,
        output_path: Path,
        translated_pages: list[tuple[int, str]],
    ) -> None:
        """Create PDF with semi-transparent translation overlay.
        
        Original document visible underneath with translated text overlaid.
        Uses proportional sizing based on page dimensions.
        """
        doc = fitz.open(source_path)
        
        try:
            translations = {page_num: text for page_num, text in translated_pages}
            
            for page_num in range(len(doc)):
                if page_num not in translations:
                    continue
                
                page = doc[page_num]
                translated_text = translations[page_num]
                
                if not translated_text.strip():
                    continue
                
                rect = page.rect
                
                # Scale proportionally to page size (reference: 600pt standard)
                scale = min(rect.width, rect.height) / 600.0
                scale = max(0.5, min(scale, 3.0))  # Clamp between 0.5x and 3x
                
                # Proportional margins
                margin = int(30 * scale)
                
                # Semi-transparent white overlay (original visible underneath)
                shape = page.new_shape()
                shape.draw_rect(rect)
                shape.finish(color=None, fill=(1, 1, 1), fill_opacity=0.7)
                shape.commit()
                
                # Text area
                text_rect = fitz.Rect(
                    margin,
                    margin,
                    rect.width - margin,
                    rect.height - margin,
                )
                
                # Scale font size based on page size and text length
                base_fontsize = 12 * scale
                char_count = len(translated_text)
                
                if char_count > 2000:
                    fontsize = base_fontsize * 0.75
                elif char_count > 1000:
                    fontsize = base_fontsize * 0.85
                else:
                    fontsize = base_fontsize
                
                fontsize = max(8, min(fontsize, 48))  # Clamp between 8 and 48
                
                logger.debug(f"Overlay page {page_num+1}: scale={scale:.2f}, fontsize={fontsize:.1f}")
                
                # Insert text with dark color for visibility over semi-transparent bg
                page.insert_textbox(
                    text_rect,
                    translated_text,
                    fontsize=fontsize,
                    fontname="helv",
                    color=(0, 0, 0),  # Black text
                    align=fitz.TEXT_ALIGN_LEFT,
                )
            
            doc.save(output_path)
            logger.info(f"Created translated PDF with overlay")
        finally:
            doc.close()
    
    def get_page_count(self, pdf_path: Path) -> int:
        """Get the number of pages in a PDF."""
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count

