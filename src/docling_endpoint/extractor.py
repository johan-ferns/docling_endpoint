from docling.document_converter import DocumentConverter, PdfFormatOption, WordFormatOption
from docling.datamodel.base_models import InputFormat
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.pipeline_options import PdfPipelineOptions, ThreadedPdfPipelineOptions

from docling_endpoint.models.extraction_models import ConvertedContent, MetadataContent

from typing import Literal, Dict, Optional, Callable
from dotenv import load_dotenv
from pathlib import Path
import os
import threading

load_dotenv()


# Global converter instance for reuse (singleton pattern)
_converter_instance : Optional[DocumentConverter] = None
_converter_lock = threading.Lock()


# :TODO consider Docx PDF format option as well
# :TODO accept PDF pipeline options as well.
# :TODO logs
def get_converter():
    """Initialize and return a DocumentConverter instance."""

    global _converter_instance

    if _converter_instance is None:
        with _converter_lock:
                if _converter_instance is None:
                                    
                    docling_path = os.getenv("DOCLING_MODEL_PATH")
                    num_workers = int(os.getenv("DOCLING_MAX_WORKERS"))

                    _converter_instance = DocumentConverter(
                        format_options={
                            InputFormat.PDF : PdfFormatOption(
                                pipeline_cls=StandardPdfPipeline,
                                pipeline_options=PdfPipelineOptions(
                                    artifacts_path=Path(docling_path),
                                    do_ocr=False,
                                    do_table_structure=True,
                                    do_code_enrichment=False,  # Disable if not needed
                                    do_formula_enrichment=False,  # Disable if not needed
                                    generate_page_images=False,  # Disable if not needed
                                    generate_picture_images=False,  # Disable if not needed
                                    # ocr_batch_size=num_workers,
                                    # layout_bac_size=num_workers,
                                    # table_batch_size=num_workers,
                                    # queue_max_size=200,
                                    # batch_polling_interval_seconds=0.1,
                                    accelerator_options=AcceleratorOptions(
                                        num_threads=num_workers,
                                        device="cpu"
                                    ),
                                )
                            ),
                            InputFormat.DOCX : WordFormatOption(
                                    # often empty/default is enough unless you need overrides
                            )
                        }
                    )

    return _converter_instance

def process_document(file_path: str, 
                     output_format: Literal["markdown", "json", "text", "html"] = "markdown") -> ConvertedContent:
    """
    Process a document (PDF or DOCX) and extract content.
    
    Args:
        file_path: Path to the document file
        output_format: Desired output format (markdown, json, or text)
    
    Returns:
        Extracted content in the specified format
    """ 

    converter = get_converter()
    content = None
    
    result = converter.convert(file_path)

    metadata = MetadataContent(
                    num_pages = len(result.document.pages),
                    num_tables = len(result.document.tables),
                    num_pictures = len(result.document.pictures)
                )
    if output_format == "markdown":
        content = ConvertedContent(
                    text = result.document.export_to_markdown(),
                    metadata = metadata
        )
    elif output_format == "text":
        content = ConvertedContent(
                text = result.document.export_to_text(),
                metadata = metadata
        )
    elif output_format == "json":
        content = ConvertedContent(
                text = result.document.export_to_dict(),
                metadata = metadata
        )
    elif output_format == "html":
        content = ConvertedContent(
                text = result.document.export_to_html(),
                metadata = metadata
        )
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    
    return content



def reset_converter():
    """
    Reset the global converter instance.
    Useful for testing or when you need to reinitialize with different settings.
    """
    global _converter_instance
    with _converter_lock:
        _converter_instance = None


if __name__ == "__main__":

    print("In Main")
    print(os.getpid())
    # file_path = "data/pdf/input/example_3.pdf"
    # file_path = "data/pdf/input/Latest AI Advancements.pdf"
    file_path = "data/word/input/example_3.docx"
    result = process_document(file_path=file_path)

    print(result)