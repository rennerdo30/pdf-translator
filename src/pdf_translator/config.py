"""Configuration management for PDF Translator."""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    """Configuration for the PDF translator."""
    
    # API settings
    api_url: str = field(default_factory=lambda: os.getenv(
        "OPENAI_BASE_URL", "http://localhost:1234/v1"
    ))
    api_key: str = field(default_factory=lambda: os.getenv(
        "OPENAI_API_KEY", "lm-studio"
    ))
    model: str = field(default_factory=lambda: os.getenv(
        "PDF_TRANSLATOR_MODEL", ""
    ))
    
    # Vision model settings
    use_vision: bool = field(default_factory=lambda: os.getenv(
        "PDF_TRANSLATOR_USE_VISION", "true"
    ).lower() == "true")
    vision_model: str = field(default_factory=lambda: os.getenv(
        "PDF_TRANSLATOR_VISION_MODEL", ""
    ))
    
    # Translation settings
    source_language: str = "auto"
    target_language: str = "english"
    
    # Processing settings
    max_tokens_per_chunk: int = 2000
    ocr_threshold: int = 50  # Minimum chars per page to consider it has text
    
    # Output settings
    output_path: Optional[str] = None
    
    def get_model(self) -> str:
        """Get the model to use, with fallback."""
        return self.model or "default"
    
    def get_vision_model(self) -> str:
        """Get the vision model to use."""
        return self.vision_model or self.model or "default"
