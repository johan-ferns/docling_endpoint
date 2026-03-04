from fastapi.responses import JSONResponse

from docling_endpoint.extractor import get_converter, process_document
from docling_endpoint.models.extraction_models import ConvertedContent

from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
from typing import Literal
import tempfile
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Docling Document Extraction API",
    description="API for extracting content",
    version="1.0.0",
    openapi_version="3.1.0",
    docs_url="/docs"
)


@app.get("/")
def read_root():
    return {"Hello" : "User",
            "message" : "Docling Document Extraction API"}


@app.on_event("startup")
async def startup_event():
    """Preload Document Converter."""
    logger.info("-"*60)
    logger.info("🚀 FastAPI application starting up...")
    logger.info("="*60)
    logger.info(f"📁 DOCLING_MODEL_PATH: {os.getenv('DOCLING_MODEL_PATH')}")
    logger.info("="*60)

    try:
        logger.info("⏳ Starting model preload...")
        # Initialize converter
        converter = get_converter()
        logger.info("✅ Model preloaded successfully!")
        logger.info("="*60)
    except Exception as e:
        logger.error(f"❌ Failed to preload model: {e}", exc_info=True)
        raise

@app.post("/upload/extract")
async def extract_dociment(
    file : UploadFile = File(...),
    output_format : Literal["markdown", "json", "text", "html"] = "markdown"
):
    """
    Upload a PDF or Word document and extract its content.
    
    Args:
        file: The document file (PDF or DOCX)
        output_format: Format of the extracted content (markdown, json, or text)
    
    Returns:
         Extracted content in the specified format
    """

    # Validate file types
    allowed_extensions = {".pdf", ".docx"}
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        logger.warning(f"⚠️ Invalid file type: {file_extension}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Only PDF and DOCX files are allowed. Got : {file_extension}"
        )

    try:
        logger.info(f"💾 Creating temporary file for {file.filename}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Read content
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        logger.info(f"📄 Processing document: {temp_file_path}")
        result : ConvertedContent = process_document(temp_file_path, output_format)
        logger.info(f"✅ Document processed successfully: {file.filename}")

        return JSONResponse(content={
            "filename" : file.filename,
            "file_type" : file_extension.lstrip("."),
            "output_format" : output_format,
            "content" : result.model_dump_json()
        })

    except Exception as e:
        logger.error(f"❌ Error processing document {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500,
                            detail=f"Error processing document : {str(e)}"
        )
    
    finally:
        # Clean up temporary files
        if temp_file_path or os.path.exists(temp_file_path):
            logger.info(f"🗑️ Cleaning up temporary file: {temp_file_path}")
            os.unlink(temp_file_path)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    logger.info("🏥 Health check endpoint accessed")
    if os.path.exists(os.getenv("DOCLING_MODEL_PATH")):
        logger.info(f"✅ Health check passed - model path exists: {model_path}")
        return {"status": "healthy", "service": "docling-endpoint-active"}
    else:
        logger.error(f"❌ Health check failed - model path not found: {model_path}")
        return {"status" : "not well", "service" : "model-path-not-found"}