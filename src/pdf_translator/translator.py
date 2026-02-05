"""Translation service using OpenAI-compatible API with vision support."""

import base64
import logging
from typing import Any

from openai import OpenAI

from pdf_translator.config import Config

logger = logging.getLogger("pdf_translator.translator")


class Translator:
    """Handles text and image translation using OpenAI-compatible API."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            base_url=config.api_url,
            api_key=config.api_key,
        )
        logger.info(f"Translator initialized with API: {config.api_url}")
    
    def translate_text(self, text: str) -> str:
        """Translate text from source to target language.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text
        """
        if not text.strip():
            logger.debug("Empty text, skipping translation")
            return ""
        
        source = self.config.source_language
        target = self.config.target_language
        
        logger.info(f"Translating text ({len(text)} chars): {source} -> {target}")
        
        if source.lower() == "auto":
            system_prompt = f"""You are a professional translator. Translate the following text to {target}.
Only output the translated text, nothing else. Preserve the original formatting and structure."""
        else:
            system_prompt = f"""You are a professional translator. Translate the following text from {source} to {target}.
Only output the translated text, nothing else. Preserve the original formatting and structure."""
        
        logger.debug(f"Calling API with model: {self.config.get_model()}")
        
        response = self.client.chat.completions.create(
            model=self.config.get_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.3,
        )
        
        result = _extract_response_text(response)
        if not result:
            logger.warning("Text translation returned empty content")
            return ""

        logger.info(f"Translation complete: {len(result)} chars output")
        logger.debug(f"Translation preview: {result[:100]}...")
        
        return result
    
    def translate_image(self, image_bytes: bytes) -> str:
        """Translate text in an image using a vision model.
        
        This is useful for scanned documents where OCR might not be ideal.
        Requires a vision-capable model like LLaVA in LM Studio.
        
        Args:
            image_bytes: PNG image bytes
            
        Returns:
            Translated text from the image
        """
        source = self.config.source_language
        target = self.config.target_language
        
        logger.info(f"Vision translation: {len(image_bytes)} bytes image, {source} -> {target}")
        
        # Encode image to base64
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        
        # Make the translation instruction very explicit
        if source.lower() == "auto":
            prompt = f"""You are a professional translator. This image contains a document.

YOUR TASK: Read all text in the image and TRANSLATE it into {target.upper()}.

IMPORTANT RULES:
1. You MUST translate ALL text to {target} - do NOT output the original language
2. Output ONLY the translated text in {target}
3. Preserve the structure and formatting of the original document
4. Do not add explanations, descriptions, or commentary
5. Do not include any text that is not a translation

Begin the translation now:"""
        else:
            prompt = f"""You are a professional translator. This image contains a document in {source}.

YOUR TASK: Read all the {source} text and TRANSLATE it into {target.upper()}.

IMPORTANT RULES:
1. You MUST translate ALL text from {source} to {target} - do NOT output {source}
2. Output ONLY the translated text in {target}
3. Preserve the structure and formatting of the original document
4. Do not add explanations, descriptions, or commentary
5. Do not include any text that is not a translation

Begin the translation now:"""
        
        response = self.client.chat.completions.create(
            model=self.config.get_vision_model(),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}",
                            },
                        },
                    ],
                },
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        
        result = _extract_response_text(response)
        if not result:
            logger.warning("Vision translation returned empty content")
            return ""

        logger.info(f"Vision translation complete: {len(result)} chars output")
        logger.debug(f"Vision translation preview: {result[:100]}...")
        
        return result
    
    def translate_chunks(self, chunks: list[str]) -> list[str]:
        """Translate multiple text chunks.
        
        Args:
            chunks: List of text chunks to translate
            
        Returns:
            List of translated chunks
        """
        return [self.translate_text(chunk) for chunk in chunks]


def translate_text_with_chunking(
    translator: Translator,
    text: str,
    max_chars: int = 2000,
) -> str:
    """Translate long text safely by chunking it first."""
    if not text.strip():
        return ""

    translated_chunks = []
    for chunk in chunk_text(text, max_chars=max_chars):
        translated = translator.translate_text(chunk)
        if translated:
            translated_chunks.append(translated)

    return "\n\n".join(translated_chunks)


def chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    """Split text into chunks for API processing.
    
    Tries to split on paragraph boundaries for better context.
    
    Args:
        text: Text to split
        max_chars: Maximum characters per chunk
        
    Returns:
        List of text chunks
    """
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    paragraphs = text.split("\n\n")
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_chars:
            if current_chunk:
                current_chunk += "\n\n"
            current_chunk += para
        else:
            if current_chunk:
                chunks.append(current_chunk)
            
            # Handle paragraphs longer than max_chars
            if len(para) > max_chars:
                sentences = para.replace(". ", ".\n").split("\n")
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 <= max_chars:
                        if current_chunk:
                            current_chunk += " "
                        current_chunk += sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sentence
            else:
                current_chunk = para
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def _extract_response_text(response: Any) -> str:
    """Extract text content from a chat completion response."""
    if response is None:
        return ""

    choices = getattr(response, "choices", None)
    if not choices:
        return ""

    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None)

    if isinstance(content, str):
        return content.strip()
    if content is None:
        return ""

    # Some APIs may return a list of content parts.
    if isinstance(content, list):
        parts = []
        for part in content:
            text = None
            if isinstance(part, dict):
                text = part.get("text")
            else:
                text = getattr(part, "text", None)
            if text:
                parts.append(text)
        return "".join(parts).strip()

    return str(content).strip()
