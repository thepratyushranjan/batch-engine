import os
import sys
import uvicorn
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from google.adk.cli.fast_api import get_fast_api_app
from config import config
from services.record_service import (
    record_service,
    InvalidRecordIdError,
    RecordNotFoundError,
    NoDataProvidedError
)
from utils.file_utils import FileProcessingError
from db.schemas import HealthResponse, DBConnectionResponse, UpdateRecordResponse

# --- Base setup ---
AGENT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(AGENT_DIR)

# Set Google Application Credentials from config
if config.google_application_credentials:
    credentials_path = os.path.join(os.path.dirname(__file__), config.google_application_credentials)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    print(f"Using credentials from: {credentials_path}")


# --- Initialize FastAPI app ---
app: FastAPI = get_fast_api_app(
    allow_origins=["*"],
    web=True,
    agents_dir=AGENT_DIR,
)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="healthy", message="Server is running")


@app.get("/db-test", response_model=DBConnectionResponse)
async def test_db() -> DBConnectionResponse:
    """Test MongoDB connection only"""
    return await record_service.check_db_connection()


@app.patch("/records/{id}", response_model=UpdateRecordResponse)
async def update_record_with_csv(
    id: str,
    user_input: List[UploadFile] = File(default=None),
    expected_output: UploadFile = File(default=None),
    instruction_from_user: Optional[str] = Form(default=None),
    client_email_address: Optional[str] = Form(default=None)
) -> UpdateRecordResponse:
    """
    Update a record with CSV/Excel file uploads.
    - user_input: One or multiple CSV/Excel files (stores filename and column names)
    - expected_output: Single CSV/Excel file (stores filename and column names)
    """
    try:
        return await record_service.update_record(
            record_id=id,
            user_input=user_input,
            expected_output=expected_output,
            instruction_from_user=instruction_from_user,
            client_email_address=client_email_address
        )
    except InvalidRecordIdError:
        raise HTTPException(status_code=400, detail="Invalid record ID format")
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="Record not found")
    except NoDataProvidedError:
        raise HTTPException(status_code=400, detail="No data provided for update")
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Entry point ---
if __name__ == "__main__":
    print("Starting FastAPI server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )
