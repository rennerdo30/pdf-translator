#!/usr/bin/env python3
"""Direct launcher for PDF Translator GUI.

Run this file directly to start the application:
    python run.py
    
Or with CLI mode:
    python run.py --cli input.pdf -t english
"""

import sys
from pathlib import Path

# Add src to path for direct execution
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))


def main():
    """Launch the application."""
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # CLI mode: remove --cli flag and run CLI
        sys.argv.pop(1)
        from pdf_translator.cli import main as cli_main
        cli_main()
    else:
        # Default: GUI mode
        from pdf_translator.gui import main as gui_main
        gui_main()


if __name__ == "__main__":
    main()
