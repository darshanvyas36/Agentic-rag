from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Schema for document metadata stored in MongoDB
class Document(BaseModel):
    id: str = Field(alias="_id")
    filename: str
    upload_date: datetime
    file_size: int

    class Config:
        # Allows Pydantic to work with MongoDB's '_id' field
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}


# Schema for the response when a document is successfully uploaded
class DocumentUploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str