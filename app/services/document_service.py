import io
from docx import Document as DocxDocument
from pypdf import PdfReader
from fastapi import UploadFile, HTTPException, status
from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_text_from_docx(file_content: bytes) -> str:
    """Extracts text from a .docx file."""
    try:
        doc = DocxDocument(io.BytesIO(file_content))
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error processing DOCX file: {e}",
        )

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extracts text from a .pdf file."""
    try:
        reader = PdfReader(io.BytesIO(file_content))
        return "\n".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error processing PDF file: {e}",
        )

def get_text_chunks(text: str) -> list[str]:
    """Splits text into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200, # Provides context between chunks
        length_function=len
    )
    return text_splitter.split_text(text)


async def process_document_file(file: UploadFile) -> list[str]:
    """
    Validates file type, extracts text, and splits it into chunks.
    """
    # Read file content into memory
    file_content = await file.read()
    
    # Determine the file type and extract text accordingly
    if file.content_type == "application/pdf":
        raw_text = extract_text_from_pdf(file_content)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        raw_text = extract_text_from_docx(file_content)
    else:
        # Handle unsupported file types
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Please upload a PDF or DOCX.",
        )

    if not raw_text or not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract text from the document. It might be empty or scanned.",
        )

    # Split the extracted text into chunks
    text_chunks = get_text_chunks(raw_text)
    return text_chunks