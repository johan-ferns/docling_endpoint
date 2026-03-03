from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.datamodel.pipeline_options import PdfPipelineOptions

from docling_endpoint.models.extraction_models import ConvertedContent, MetadataContent

from typing import Literal, Dict
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

# :TODO consider Docx PDF format option as well
# :TODO accept PDF pipeline options as well.
def get_converter():
    """Initialize and return a DocumentConverter instance."""
    docling_path = os.getenv("DOCLING_MODEL_PATH")
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF : PdfFormatOption(
                pipeline_cls=StandardPdfPipeline,
                pipeline_options=PdfPipelineOptions(
                    artifacts_path=Path(docling_path),
                    do_ocr=False
                )
            )
        }
    )

    return converter

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