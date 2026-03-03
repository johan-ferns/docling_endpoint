from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.datamodel.pipeline_options import PdfPipelineOptions

from docling_endpoint.models.extraction_models import ConvertedContent, MetadataContent

from typing import Literal, Dict, Optional
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
                                    do_ocr=False
                                )
                            )
                        },
                        max_num_threads=num_workers
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
    result = converter.convert(file_path)

    metadata = MetadataContent(
                    num_pages = len(result.document.pages),
                    num_tables = len(result.document.tables),
                    num_pictures = len(result.document.pictures)
                )
    if output_format == "markdown":
        return ConvertedContent(
                text = result.document.export_to_markdown(),
                metadata = metadata
        )
    elif output_format == "text":
        return ConvertedContent(
                text = result.document.export_to_text(),
                metadata = metadata
        )
    elif output_format == "json":
        return ConvertedContent(
                text = result.document.export_to_dict(),
                metadata = metadata
        )
    elif output_format == "html":
        return ConvertedContent(
                text = result.document.export_to_html(),
                metadata = metadata
        )
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def reset_converter():
    """
    Reset the global converter instance.
    Useful for testing or when you need to reinitialize with different settings.
    """
    global _converter_instance
    with _converter_lock:
        _converter_instance = None