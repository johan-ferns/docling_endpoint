from docling_endpoint.extractor import process_document

from docling_endpoint.models.extraction_models import ConvertedContent

from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
from typing import Literal
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Docling Document Extraction API",
    description="API for extracting content",
    version="1.0.0",
    swagger="2.0"
)


app.get("/")
def read_root():
    return {"Hello" : "User",
            "message" : "Docling Document Extraction API"}


app.post("/upload/extract")
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
    file_extension = Path(file.filename).suffux.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Only PDF and DOCX files are allowed. Got : {file_extension}"
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Read content
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        result : ConvertedContent = process_document(temp_file_path, output_format)

        return JSONresponse(content={
            "filename" : file.filename,
            "file_type" : file_extension.lstrip("."),
            "output_format" : output_format,
            "content" : result.model_dump_json()
        })

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error processing document : {str(e)}"
        )

@app.get("/health")
def health_check():
    """Health check endpoint"""
    if os.path.exists(os.getenv("DOCLING_MODEL_PATH")):
        return {"status": "healthy", "service": "docling-endpoint-active"}
    else:
        return {"status" : "not well", "service" : "model-path-not-found"}