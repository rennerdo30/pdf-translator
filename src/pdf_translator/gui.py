"""Simple GUI for PDF Translator using Tkinter."""

import threading
from pathlib import Path
from tkinter import (
    Tk, Frame, Label, Entry, Button, StringVar, filedialog,
    messagebox, ttk, Text, Scrollbar, END, DISABLED, NORMAL
)

from pdf_translator.config import Config
from pdf_translator.pdf_handler import PDFHandler
from pdf_translator.ocr import OCRProcessor
from pdf_translator.translator import Translator, translate_text_with_chunking


class PDFTranslatorGUI:
    """Simple GUI for PDF translation."""
    
    def __init__(self):
        self.root = Tk()
        self.root.title("PDF Translator")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)
        
        # Variables
        self.input_file = StringVar()
        self.output_file = StringVar()
        self.source_lang = StringVar(value="auto")
        self.target_lang = StringVar(value="english")
        self.api_url = StringVar(value="http://localhost:1234/v1")
        self.api_key = StringVar(value="lm-studio")
        self.model = StringVar()
        self.use_vision = StringVar(value="1")
        
        self.is_translating = False
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the GUI layout."""
        # Main container with padding
        main_frame = Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title = Label(main_frame, text="PDF Translator", font=("Helvetica", 18, "bold"))
        title.pack(pady=(0, 20))
        
        # File selection frame
        file_frame = Frame(main_frame)
        file_frame.pack(fill="x", pady=5)
        
        Label(file_frame, text="Input PDF:", width=12, anchor="w").pack(side="left")
        Entry(file_frame, textvariable=self.input_file, width=40).pack(side="left", padx=5, expand=True, fill="x")
        Button(file_frame, text="Browse", command=self._browse_input).pack(side="left")
        
        # Output file
        output_frame = Frame(main_frame)
        output_frame.pack(fill="x", pady=5)
        
        Label(output_frame, text="Output PDF:", width=12, anchor="w").pack(side="left")
        Entry(output_frame, textvariable=self.output_file, width=40).pack(side="left", padx=5, expand=True, fill="x")
        Button(output_frame, text="Browse", command=self._browse_output).pack(side="left")
        
        # Language selection
        lang_frame = Frame(main_frame)
        lang_frame.pack(fill="x", pady=10)
        
        Label(lang_frame, text="Source:", width=12, anchor="w").pack(side="left")
        source_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.source_lang,
            values=["auto", "english", "german", "french", "spanish", "japanese", "chinese", "korean"],
            width=15,
        )
        source_combo.pack(side="left", padx=5)
        
        Label(lang_frame, text="Target:", width=8, anchor="w").pack(side="left", padx=(20, 0))
        target_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.target_lang,
            values=["english", "german", "french", "spanish", "japanese", "chinese", "korean"],
            width=15,
        )
        target_combo.pack(side="left", padx=5)
        
        # API Settings
        api_frame = Frame(main_frame)
        api_frame.pack(fill="x", pady=5)
        
        Label(api_frame, text="API URL:", width=12, anchor="w").pack(side="left")
        Entry(api_frame, textvariable=self.api_url, width=50).pack(side="left", padx=5, expand=True, fill="x")
        
        # Model setting
        model_frame = Frame(main_frame)
        model_frame.pack(fill="x", pady=5)
        
        Label(model_frame, text="Model:", width=12, anchor="w").pack(side="left")
        Entry(model_frame, textvariable=self.model, width=30).pack(side="left", padx=5)
        Label(model_frame, text="(leave empty for default)", fg="gray").pack(side="left")
        
        # Vision checkbox
        vision_frame = Frame(main_frame)
        vision_frame.pack(fill="x", pady=5)
        
        ttk.Checkbutton(
            vision_frame,
            text="Use vision model for scanned pages (recommended for LM Studio)",
            variable=self.use_vision,
            onvalue="1",
            offvalue="0",
        ).pack(side="left")
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode="determinate", length=400)
        self.progress.pack(fill="x", pady=15)
        
        # Status label
        self.status_label = Label(main_frame, text="Ready", fg="gray")
        self.status_label.pack()
        
        # Translate button
        self.translate_btn = Button(
            main_frame,
            text="Translate PDF",
            command=self._start_translation,
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=10,
        )
        self.translate_btn.pack(pady=20)
        
        # Log area
        log_frame = Frame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        Label(log_frame, text="Log:", anchor="w").pack(anchor="w")
        
        scrollbar = Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.log_text = Text(log_frame, height=8, yscrollcommand=scrollbar.set, state=DISABLED)
        self.log_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.log_text.yview)
    
    def _browse_input(self):
        """Open file dialog for input PDF."""
        filename = filedialog.askopenfilename(
            title="Select PDF to translate",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if filename:
            self.input_file.set(filename)
            # Auto-set output filename
            path = Path(filename)
            self.output_file.set(str(path.parent / f"{path.stem}_translated.pdf"))
    
    def _browse_output(self):
        """Open file dialog for output PDF."""
        filename = filedialog.asksaveasfilename(
            title="Save translated PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if filename:
            self.output_file.set(filename)
    
    def _log(self, message: str):
        """Add message to log area."""
        if threading.current_thread() is not threading.main_thread():
            self.root.after(0, self._log, message)
            return

        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, message + "\n")
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)
    
    def _update_status(self, message: str):
        """Update status label."""
        if threading.current_thread() is not threading.main_thread():
            self.root.after(0, self._update_status, message)
            return

        self.status_label.config(text=message)
        self.root.update_idletasks()

    def _set_progress(self, value: float):
        """Update progress value safely from any thread."""
        if threading.current_thread() is not threading.main_thread():
            self.root.after(0, self._set_progress, value)
            return

        self.progress["value"] = max(0, min(value, 100))

    def _set_translate_button_state(self, state: str):
        """Set translate button state safely from any thread."""
        if threading.current_thread() is not threading.main_thread():
            self.root.after(0, self._set_translate_button_state, state)
            return

        self.translate_btn.config(state=state)

    def _show_info(self, title: str, message: str):
        """Show info dialog safely from any thread."""
        if threading.current_thread() is not threading.main_thread():
            self.root.after(0, self._show_info, title, message)
            return

        messagebox.showinfo(title, message)

    def _show_error(self, title: str, message: str):
        """Show error dialog safely from any thread."""
        if threading.current_thread() is not threading.main_thread():
            self.root.after(0, self._show_error, title, message)
            return

        messagebox.showerror(title, message)
    
    def _start_translation(self):
        """Start translation in a background thread."""
        if self.is_translating:
            return
        
        # Validate inputs
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input PDF file.")
            return
        
        if not Path(self.input_file.get()).exists():
            messagebox.showerror("Error", "Input file does not exist.")
            return
        
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output file.")
            return
        
        if not self.target_lang.get():
            messagebox.showerror("Error", "Please select a target language.")
            return

        input_path = Path(self.input_file.get())
        output_path = Path(self.output_file.get())

        if input_path.resolve() == output_path.resolve():
            messagebox.showerror("Error", "Output file must be different from input file.")
            return
        
        self.is_translating = True
        self._set_translate_button_state(DISABLED)
        self._set_progress(0)
        
        # Run translation in background thread
        job = {
            "input_file": str(input_path),
            "output_file": str(output_path),
            "api_url": self.api_url.get(),
            "api_key": self.api_key.get(),
            "model": self.model.get(),
            "source_language": self.source_lang.get(),
            "target_language": self.target_lang.get(),
            "use_vision": self.use_vision.get(),
        }
        thread = threading.Thread(target=self._do_translation, args=(job,), daemon=True)
        thread.start()
    
    def _do_translation(self, job: dict[str, str]):
        """Perform the translation (runs in background thread)."""
        try:
            input_path = Path(job["input_file"])
            output_path = Path(job["output_file"])
            
            # Build config
            config = Config(
                api_url=job["api_url"],
                api_key=job["api_key"] or "lm-studio",
                model=job["model"],
                source_language=job["source_language"],
                target_language=job["target_language"],
                use_vision=job["use_vision"] == "1",
            )
            
            self._log(f"Starting translation...")
            self._log(f"  Source: {config.source_language}")
            self._log(f"  Target: {config.target_language}")
            self._log(f"  Vision: {'enabled' if config.use_vision else 'disabled'}")
            
            # Initialize components
            pdf_handler = PDFHandler(config)
            translator = Translator(config)
            ocr_processor = None
            
            if not config.use_vision:
                ocr_processor = OCRProcessor(config.source_language)
                if not ocr_processor.is_available():
                    self._log("Warning: Tesseract OCR not available. Falling back to vision mode.")
                    config.use_vision = True
                    ocr_processor = None
            
            # Get page count
            page_count = pdf_handler.get_page_count(input_path)
            self._log(f"Processing {page_count} pages...")
            
            translated_pages = []
            
            for i, page_data in enumerate(pdf_handler.extract_pages(input_path)):
                self._update_status(f"Translating page {i + 1}/{page_count}...")
                if page_count:
                    self._set_progress((i / page_count) * 100)
                
                translated_text = ""
                
                if config.use_vision and page_data.image_bytes:
                    # Use vision model
                    try:
                        translated_text = translator.translate_image(page_data.image_bytes)
                        self._log(f"  Page {i + 1}: Vision translation complete")
                    except Exception as e:
                        self._log(f"  Page {i + 1}: Vision failed - {e}")
                        if page_data.text_blocks:
                            page_text = "\n\n".join(b.text for b in page_data.text_blocks)
                            translated_text = translate_text_with_chunking(
                                translator,
                                page_text,
                                max_chars=config.max_tokens_per_chunk,
                            )
                
                elif page_data.has_text:
                    # Extract and translate text
                    page_text = "\n\n".join(block.text for block in page_data.text_blocks)
                    translated_text = translate_text_with_chunking(
                        translator,
                        page_text,
                        max_chars=config.max_tokens_per_chunk,
                    )
                    self._log(f"  Page {i + 1}: Text translation complete")
                
                elif ocr_processor and page_data.image_bytes:
                    # Use OCR
                    try:
                        ocr_text = ocr_processor.extract_text(page_data.image_bytes)
                        if ocr_text.strip():
                            translated_text = translate_text_with_chunking(
                                translator,
                                ocr_text,
                                max_chars=config.max_tokens_per_chunk,
                            )
                            self._log(f"  Page {i + 1}: OCR + translation complete")
                    except Exception as e:
                        self._log(f"  Page {i + 1}: OCR failed - {e}")
                
                translated_pages.append((page_data.page_num, translated_text))
            
            # Create output PDF
            self._update_status("Creating output PDF...")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            pdf_handler.create_translated_pdf(input_path, output_path, translated_pages)
            
            self._set_progress(100)
            self._update_status("Translation complete!")
            self._log(f"\n✓ Saved to: {output_path}")
            
            self._show_info("Success", f"Translation complete!\n\nSaved to:\n{output_path}")
            
        except Exception as e:
            self._log(f"\n✗ Error: {e}")
            self._update_status("Error occurred")
            self._show_error("Error", f"Translation failed:\n\n{e}")
        
        finally:
            self.is_translating = False
            self._set_translate_button_state(NORMAL)
    
    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop()


def main():
    """Launch the GUI."""
    app = PDFTranslatorGUI()
    app.run()


if __name__ == "__main__":
    main()
