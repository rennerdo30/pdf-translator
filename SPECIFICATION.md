# PDF Translator - Specification

## Overview
Cross-platform PDF translator using AI vision models for high-quality translation of scanned documents.

## Features

### Translation
- **Vision Model Translation**: Sends page images directly to vision models for OCR + translation
- **Text Extraction**: Falls back to native PDF text when available
- **OCR Support**: Tesseract OCR as alternative to vision models
- **Chunking**: Automatic text chunking for API token limits

### Output Modes
- **Side-by-Side**: Original page → Translation page (same dimensions)
- **Overlay**: Semi-transparent overlay preserving original with translated text

### Proportional Scaling
- Fonts and margins scale with page dimensions
- Handles unusual page sizes (receipts, tickets, large documents)
- Reference: 600pt standard → 12pt base font

### Interfaces
- **CLI**: `pdf-translate` with Rich progress bar
- **GUI**: `pdf-translate-gui` Tkinter interface

## Technical Details

### Dependencies
| Package | Purpose |
|---------|---------| 
| PyMuPDF | PDF rendering and manipulation |
| pytesseract | OCR fallback |
| openai | API client |
| click | CLI framework |
| rich | Terminal UI |
| Pillow | Image processing |

### API Compatibility
- OpenAI: `https://api.openai.com/v1`
- LM Studio: `http://localhost:1234/v1` (default)
- Ollama: `http://localhost:11434/v1`

### Recommended Vision Models
- `qwen/qwen2.5-vl-7b` (good translation quality)
- `llava-v1.6` 
- GPT-4 Vision

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY          # API key
OPENAI_BASE_URL         # API endpoint
PDF_TRANSLATOR_MODEL    # Default text model
PDF_TRANSLATOR_USE_VISION  # Enable vision (true/false)
```

## Architecture

```
src/pdf_translator/
├── __init__.py         # Package version
├── __main__.py         # Module entry (GUI default)
├── cli.py              # Click CLI with Rich progress
├── config.py           # Configuration management
├── gui.py              # Tkinter GUI
├── logging_config.py   # Logging setup
├── ocr.py              # Tesseract OCR processor
├── pdf_handler.py      # PDF extraction/reconstruction
└── translator.py       # AI translation service
```

## Version
- **0.1.0**: Initial release
  - Vision model support
  - Side-by-side and overlay modes
  - Proportional scaling
  - CLI and GUI interfaces
