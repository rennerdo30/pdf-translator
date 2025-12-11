"""Main entry point for running as a module.

Usage:
    python -m pdf_translator          # Launch GUI
    python -m pdf_translator --cli    # Show CLI help
    python -m pdf_translator --cli input.pdf -t english  # CLI mode
"""

import sys

def main():
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
