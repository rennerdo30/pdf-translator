# PDF Translator

[![CI](https://github.com/rennerdo30/pdf-translator/actions/workflows/ci.yml/badge.svg)](https://github.com/rennerdo30/pdf-translator/actions/workflows/ci.yml)
[![Release](https://github.com/rennerdo30/pdf-translator/actions/workflows/release.yml/badge.svg)](https://github.com/rennerdo30/pdf-translator/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A cross-platform tool that translates PDF documents using AI, with vision model support for scanned documents.

## Features

- AI-powered translation using OpenAI-compatible APIs
- Vision model translation for scanned/image PDFs
- OCR fallback via Tesseract
- GUI and CLI interfaces
- Two output modes: side-by-side and overlay
- Proportional scaling for multiple page sizes

## Installation

### Prerequisites

1. Python 3.10+
2. Optional Tesseract (for OCR mode):
   - macOS: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`
   - Windows: [UB Mannheim build](https://github.com/UB-Mannheim/tesseract/wiki)

### Setup

```bash
git clone https://github.com/rennerdo30/pdf-translator.git
cd pdf-translator
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

## Quick Start

```bash
pdf-translate input.pdf -s japanese -t english
```

GUI:

```bash
pdf-translate-gui
```

Run directly:

```bash
python run.py
python run.py --cli input.pdf -t english
```

## Output Modes

Side-by-side (default):

```bash
pdf-translate input.pdf -t german
```

Overlay mode:

```bash
pdf-translate input.pdf -t german --overlay
```

## Configuration

Environment variables:

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="http://localhost:1234/v1"
export PDF_TRANSLATOR_MODEL="gpt-4"
export PDF_TRANSLATOR_USE_VISION="true"
```

## Development

```bash
pip install -e '.[dev]'
python -m pytest
python -m compileall -q src tests
python -m build
```

## API Compatibility

| Provider | Base URL | Notes |
|----------|----------|-------|
| LM Studio | `http://localhost:1234/v1` | Default, use vision models |
| OpenAI | `https://api.openai.com/v1` | Requires API key |
| Ollama | `http://localhost:11434/v1` | Use vision models |

## Project Docs

- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Specification](SPECIFICATION.md)

## License

MIT License. See [LICENSE](LICENSE).
