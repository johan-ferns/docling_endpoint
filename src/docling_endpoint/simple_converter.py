
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.datamodel.pipeline_options import PdfPipelineOptions
from pathlib import Path

# Change this to a local path or another URL if desired.
# Note: using the default URL requires network access; if offline, provide a
# local file path (e.g., Path("/path/to/file.pdf")).
source = "data/pdf/input/example_3.pdf"
docling_path = "models/model_artifacts/complete"
converter = DocumentConverter(
    format_options = {
        InputFormat.PDF : PdfFormatOption(
            pipeline_cls=StandardPdfPipeline,
            pipeline_options=PdfPipelineOptions(
                artifacts_path=Path(docling_path),
                do_ocr=False,
                # force_backend_text=True,
                # accelerator_options=accelerator_options
                # do_table_structure=True,
                # generate_picture_images=True,
            ),
        )
    }
)
result = converter.convert(source)

# Print Markdown to stdout.
print(len(result.document.tables))