"""Command-line interface for PDF Translator."""

import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from pdf_translator.config import Config
from pdf_translator.pdf_handler import PDFHandler
from pdf_translator.ocr import OCRProcessor
from pdf_translator.translator import Translator, translate_text_with_chunking
from pdf_translator.logging_config import setup_logging

logger = logging.getLogger("pdf_translator.cli")

console = Console()


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-s", "--source",
    default="auto",
    help="Source language (default: auto-detect)",
)
@click.option(
    "-t", "--target",
    required=True,
    help="Target language (required)",
)
@click.option(
    "-o", "--output",
    type=click.Path(path_type=Path),
    help="Output file path (default: {input}_translated.pdf)",
)
@click.option(
    "--api-url",
    help="API endpoint URL (default: http://localhost:1234/v1)",
)
@click.option(
    "--api-key",
    help="API key (or set OPENAI_API_KEY env var)",
)
@click.option(
    "--model",
    help="Model name to use for text translation",
)
@click.option(
    "--vision-model",
    help="Vision model name for image-based translation",
)
@click.option(
    "--use-vision/--no-vision",
    default=True,
    help="Use vision model for scanned pages (default: enabled)",
)
@click.option(
    "--use-ocr/--no-ocr",
    default=False,
    help="Use OCR instead of vision model for scanned pages",
)
@click.option(
    "--overlay/--side-by-side",
    "overlay_mode",
    default=False,
    help="Overlay mode replaces original, side-by-side preserves original (default)",
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose logging output",
)
def main(
    input_file: Path,
    source: str,
    target: str,
    output: Optional[Path],
    api_url: Optional[str],
    api_key: Optional[str],
    model: Optional[str],
    vision_model: Optional[str],
    use_vision: bool,
    use_ocr: bool,
    overlay_mode: bool,
    verbose: bool,
) -> None:
    """Translate a PDF file using AI.
    
    INPUT_FILE: Path to the PDF file to translate.
    
    Examples:
    
        pdf-translate document.pdf -t english
        
        pdf-translate document.pdf -s japanese -t english -o output.pdf
        
        pdf-translate document.pdf -t german --api-url http://localhost:1234/v1
    """
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(level=log_level, console=True)
    logger.info(f"Starting PDF Translator (verbose={'on' if verbose else 'off'})")
    
    # Build configuration
    config = Config(
        source_language=source,
        target_language=target,
    )
    
    if api_url:
        config.api_url = api_url
    if api_key:
        config.api_key = api_key
    if model:
        config.model = model
    if vision_model:
        config.vision_model = vision_model
    
    # Handle OCR vs Vision preference
    if use_ocr:
        config.use_vision = False
    else:
        config.use_vision = use_vision
    
    # Set output path
    if output:
        config.output_path = str(output)
    else:
        output = input_file.parent / f"{input_file.stem}_translated.pdf"
        config.output_path = str(output)

    if input_file.resolve() == output.resolve():
        raise click.BadParameter(
            "Output file must be different from input file.",
            param_hint="--output",
        )
    
    console.print(f"\n[bold blue]PDF Translator[/bold blue]")
    console.print(f"  Input:  {input_file}")
    console.print(f"  Output: {output}")
    console.print(f"  Source: {source}")
    console.print(f"  Target: {target}")
    console.print(f"  API:    {config.api_url}")
    console.print(f"  Vision: {'enabled' if config.use_vision else 'disabled'}")
    console.print()
    
    # Initialize components
    pdf_handler = PDFHandler(config)
    translator = Translator(config)
    ocr_processor = None
    
    if not config.use_vision:
        ocr_processor = OCRProcessor(source)
        if not ocr_processor.is_available():
            console.print("[yellow]Warning: Tesseract OCR not available. "
                         "Falling back to vision model.[/yellow]")
            config.use_vision = True
            ocr_processor = None
    
    # Process PDF
    page_count = pdf_handler.get_page_count(input_file)
    translated_pages = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Translating pages...", total=page_count)
        
        for page_data in pdf_handler.extract_pages(input_file):
            progress.update(task, description=f"Processing page {page_data.page_num + 1}/{page_count}")
            
            translated_text = ""
            
            if page_data.has_text and not config.use_vision:
                # Page has native text - extract and translate
                page_text = "\n\n".join(block.text for block in page_data.text_blocks)
                translated_text = translate_text_with_chunking(
                    translator,
                    page_text,
                    max_chars=config.max_tokens_per_chunk,
                )
            
            elif config.use_vision and page_data.image_bytes:
                # Use vision model for direct translation
                try:
                    translated_text = translator.translate_image(page_data.image_bytes)
                except Exception as e:
                    console.print(f"[yellow]Vision model failed for page {page_data.page_num + 1}: {e}[/yellow]")
                    # Fallback to text if available
                    if page_data.has_text:
                        page_text = "\n\n".join(block.text for block in page_data.text_blocks)
                        translated_text = translate_text_with_chunking(
                            translator,
                            page_text,
                            max_chars=config.max_tokens_per_chunk,
                        )
            
            elif ocr_processor and page_data.image_bytes:
                # Use OCR for scanned pages
                try:
                    ocr_text = ocr_processor.extract_text(page_data.image_bytes)
                    if ocr_text.strip():
                        translated_text = translate_text_with_chunking(
                            translator,
                            ocr_text,
                            max_chars=config.max_tokens_per_chunk,
                        )
                except Exception as e:
                    console.print(f"[yellow]OCR failed for page {page_data.page_num + 1}: {e}[/yellow]")
            
            else:
                # Fallback: just translate whatever text we have
                if page_data.text_blocks:
                    page_text = "\n\n".join(block.text for block in page_data.text_blocks)
                    translated_text = translate_text_with_chunking(
                        translator,
                        page_text,
                        max_chars=config.max_tokens_per_chunk,
                    )
            
            translated_pages.append((page_data.page_num, translated_text))
            progress.advance(task)
    
    # Create output PDF
    console.print("\n[bold]Creating translated PDF...[/bold]")
    if overlay_mode:
        console.print("  Mode: Overlay (replacing original content)")
        Path(config.output_path).parent.mkdir(parents=True, exist_ok=True)
        pdf_handler.create_overlay_pdf(input_file, Path(config.output_path), translated_pages)
    else:
        console.print("  Mode: Side-by-side (preserving original pages)")
        Path(config.output_path).parent.mkdir(parents=True, exist_ok=True)
        pdf_handler.create_translated_pdf(input_file, Path(config.output_path), translated_pages)
    
    console.print(f"\n[bold green]✓ Translation complete![/bold green]")
    console.print(f"  Output saved to: {config.output_path}\n")


if __name__ == "__main__":
    main()
