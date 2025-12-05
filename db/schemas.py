"""
Pydantic models for request/response schemas.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class FileInfo(BaseModel):
    """Schema for file metadata stored in records"""
    filename: str
    columns: List[str]


class RecordUpdateForm(BaseModel):
    """Form fields for PATCH /records/{id} (excludes file uploads)"""
    instruction_from_user: Optional[str] = None
    client_email_address: Optional[EmailStr] = None


class RecordResponse(BaseModel):
    """Response schema for record operations"""
    id: str
    task_id: str
    user_input: Optional[List[FileInfo]] = None
    expected_output: Optional[List[str]] = None
    instruction_from_user: Optional[str] = None
    client_email_address: Optional[str] = None
    progress: int = 0
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Response schema for health check endpoint"""
    status: str
    message: str


class DBConnectionResponse(BaseModel):
    """Response schema for database connection test"""
    status: str
    message: str
    database: Optional[str] = None


class UpdateRecordData(BaseModel):
    """Data payload for update record response"""
    task_id: str
    user_input: Optional[List[FileInfo]] = None
    expected_output: Optional[List[str]] = None
    instruction_from_user: Optional[str] = None
    client_email_address: Optional[str] = None
    updated_date: str


class UpdateRecordResponse(BaseModel):
    """Response schema for record update operations"""
    status: str
    message: str
    data: Optional[UpdateRecordData] = None
