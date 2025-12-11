# PDF Translator

A cross-platform tool that translates PDF documents using AI, with vision model support for scanned documents.

## Features

- 🌐 **AI-Powered Translation** - Uses OpenAI API or compatible endpoints (LM Studio, Ollama)
- 👁️ **Vision Model Support** - Direct image-to-text translation for scanned PDFs (recommended)
- 📄 **OCR Fallback** - Tesseract OCR support when vision models unavailable
- 🖥️ **Cross-Platform** - Works on Windows, Linux, and macOS
- 📐 **Proportional Sizing** - Automatically scales output for any page size
- 🎯 **Two Output Modes** - Side-by-side or overlay

## Installation

### Prerequisites

1. **Python 3.9+** - [Download Python](https://python.org)

2. **Tesseract OCR** (optional, for `--use-ocr` mode):
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt install tesseract-ocr`
   - **Windows**: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)

### Install

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-translator.git
cd pdf-translator

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -e .
```

## Quick Start

### With LM Studio (Recommended for Local Use)

1. Start LM Studio and load a **vision model** (e.g., `qwen/qwen2.5-vl-7b`)
2. Enable the local server (default: `http://localhost:1234/v1`)
3. Translate:

```bash
pdf-translate input.pdf -s japanese -t english
```

### GUI

```bash
pdf-translate-gui
```

### Direct Python Execution

```bash
python run.py              # GUI
python run.py --cli input.pdf -t english  # CLI
```

## Output Modes

### Side-by-Side (Default)
Original page followed by translation page (same size):
```bash
pdf-translate input.pdf -t german
```

### Overlay Mode
Translation overlaid on semi-transparent original:
```bash
pdf-translate input.pdf -t german --overlay
```

## CLI Options

```
Usage: pdf-translate [OPTIONS] INPUT_FILE

Options:
  -s, --source TEXT        Source language (default: auto-detect)
  -t, --target TEXT        Target language (required)
  -o, --output PATH        Output file path
  --api-url TEXT           API endpoint URL
  --api-key TEXT           API key (or set OPENAI_API_KEY)
  --model TEXT             Model name for text translation
  --vision-model TEXT      Vision model for image translation
  --use-vision/--no-vision Use vision model (default: enabled)
  --use-ocr/--no-ocr       Use OCR instead of vision model
  --overlay/--side-by-side Output mode (default: side-by-side)
  -v, --verbose            Enable verbose logging
  --help                   Show this message and exit
```

## Configuration

Environment variables:

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="http://localhost:1234/v1"
export PDF_TRANSLATOR_MODEL="gpt-4"
export PDF_TRANSLATOR_USE_VISION="true"
```

## API Compatibility

| Provider | Base URL | Notes |
|----------|----------|-------|
| LM Studio | `http://localhost:1234/v1` | Default, use vision models |
| OpenAI | `https://api.openai.com/v1` | Requires API key |
| Ollama | `http://localhost:11434/v1` | Use vision models |

## How It Works

1. **Page Extraction** - Renders each PDF page as an image
2. **Vision Translation** - Sends image to vision model for direct translation
3. **Reconstruction** - Creates output PDF with translated content
4. **Proportional Scaling** - Adjusts fonts/margins based on page size

## Project Structure

```
pdf-translator/
├── src/pdf_translator/
│   ├── cli.py           # CLI interface
│   ├── gui.py           # Tkinter GUI
│   ├── translator.py    # AI translation
│   ├── pdf_handler.py   # PDF processing
│   ├── ocr.py           # OCR support
│   └── config.py        # Configuration
├── run.py               # Direct launcher
├── pyproject.toml       # Package config
└── README.md
```

## License

MIT License - see [LICENSE](LICENSE) for details.
