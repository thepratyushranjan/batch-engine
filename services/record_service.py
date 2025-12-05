import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

from fastapi import UploadFile
from bson import ObjectId
from config import config
from db.connection import mongodb
from utils.file_utils import extract_columns_from_file, FileProcessingError
from db.schemas import DBConnectionResponse, UpdateRecordResponse, UpdateRecordData, FileInfo

# Constants
IST = timezone(timedelta(hours=5, minutes=30))


class InvalidRecordIdError(Exception):
    """Raised when record ID format is invalid"""
    pass


class RecordNotFoundError(Exception):
    """Raised when record is not found"""
    pass


class NoDataProvidedError(Exception):
    """Raised when no update data is provided"""
    pass


def get_ist_datetime() -> datetime:
    """Get current datetime in IST as naive datetime for MongoDB"""
    return datetime.now(IST).replace(tzinfo=None)


def validate_object_id(record_id: str) -> ObjectId:
    """Validate and convert string ID to ObjectId"""
    try:
        return ObjectId(record_id)
    except Exception:
        raise InvalidRecordIdError("Invalid record ID format")


class RecordService:
    """Service for handling record-related business operations"""
    
    def __init__(self):
        self._collection = None
    
    async def _get_collection(self):
        """Get MongoDB collection with lazy connection"""
        if self._collection is None:
            await mongodb.connect_db()
            self._collection = mongodb.get_collection(config.mongodb_collection)
        return self._collection
    
    async def _process_file(self, file: UploadFile) -> FileInfo:
        """Process a single file and extract columns"""
        content = await file.read()
        file_data = extract_columns_from_file(content, file.filename)
        return FileInfo(filename=file_data["filename"], columns=file_data["columns"])
    
    async def _process_input_files(self, files: List[UploadFile]) -> List[FileInfo]:
        """Process multiple input files"""
        return [
            await self._process_file(file)
            for file in files
            if file.filename
        ]
    
    async def _build_update_data(
        self,
        user_input: Optional[List[UploadFile]],
        expected_output: Optional[UploadFile],
        instruction_from_user: Optional[str],
        client_email_address: Optional[str]
    ) -> Dict[str, Any]:
        """Build update data dictionary from provided inputs"""
        update_data = {}
        user_input_files: Optional[List[FileInfo]] = None
        expected_output_columns: Optional[List[str]] = None
        
        # Process user input files
        if user_input:
            input_files_data = await self._process_input_files(user_input)
            if input_files_data:
                user_input_files = input_files_data
                update_data["user_input"] = [f.model_dump() for f in input_files_data]
        
        # Process expected output file
        if expected_output and expected_output.filename:
            file_data = await self._process_file(expected_output)
            expected_output_columns = file_data.columns
            update_data["expected_output"] = file_data.columns
        
        # Add optional text fields
        if instruction_from_user is not None:
            update_data["instruction_from_user"] = instruction_from_user
        if client_email_address is not None:
            update_data["client_email_address"] = client_email_address
        
        if not update_data:
            raise NoDataProvidedError("No data provided for update")
        
        # Add auto-generated fields
        update_data["task_id"] = str(uuid.uuid4())
        update_data["updated_date"] = get_ist_datetime()
        
        # Store typed data for response building
        update_data["_user_input_files"] = user_input_files
        update_data["_expected_output_columns"] = expected_output_columns
        
        return update_data
    
    async def update_record(
        self,
        record_id: str,
        user_input: Optional[List[UploadFile]] = None,
        expected_output: Optional[UploadFile] = None,
        instruction_from_user: Optional[str] = None,
        client_email_address: Optional[str] = None
    ) -> UpdateRecordResponse:
        """Update a record with optional CSV/Excel file uploads"""
        obj_id = validate_object_id(record_id)
        collection = await self._get_collection()
        
        # Verify record exists
        if not await collection.find_one({"_id": obj_id}):
            raise RecordNotFoundError("Record not found")
        
        # Build and apply update
        update_data = await self._build_update_data(
            user_input, expected_output, instruction_from_user, client_email_address
        )
        
        # Extract typed data before DB update
        user_input_files = update_data.pop("_user_input_files", None)
        expected_output_columns = update_data.pop("_expected_output_columns", None)
        
        result = await collection.update_one({"_id": obj_id}, {"$set": update_data})
        
        if result.modified_count == 0:
            return UpdateRecordResponse(status="unchanged", message="No changes made to the record")
        
        # Build typed response
        response_data = UpdateRecordData(
            task_id=update_data["task_id"],
            user_input=user_input_files,
            expected_output=expected_output_columns,
            instruction_from_user=update_data.get("instruction_from_user"),
            client_email_address=update_data.get("client_email_address"),
            updated_date=update_data["updated_date"].isoformat()
        )
        
        return UpdateRecordResponse(
            status="success",
            message="Record updated successfully",
            data=response_data
        )
    
    async def check_db_connection(self) -> DBConnectionResponse:
        """Test MongoDB connection"""
        try:
            await self._get_collection()
            await mongodb.client.admin.command("ping")
            return DBConnectionResponse(
                status="connected",
                message="MongoDB connection successful",
                database=config.mongodb_database
            )
        except Exception as e:
            return DBConnectionResponse(status="error", message=str(e))


record_service = RecordService()