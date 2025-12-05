# Implementation Plan

- [x] 1. Add new Pydantic response model to schemas.py
  - Add `UpdateRecordResponse` model with `status`, `message`, and optional `data` fields
  - Import `RecordResponse` for the nested data field type
  - _Requirements: 3.1, 4.1_

- [x] 2. Update FastAPI endpoints in main.py to use response models
  - [x] 2.1 Import Pydantic models from schemas.py
    - Add imports for `HealthResponse`, `DBConnectionResponse`, `UpdateRecordResponse`
    - _Requirements: 1.1, 2.1, 3.1_
  - [x] 2.2 Update health_check endpoint with response_model
    - Add `response_model=HealthResponse` to decorator
    - Return `HealthResponse` instance instead of dict
    - _Requirements: 1.1, 1.2_
  - [x] 2.3 Update test_db endpoint with response_model
    - Add `response_model=DBConnectionResponse` to decorator
    - _Requirements: 2.1_
  - [x] 2.4 Update update_record_with_csv endpoint with response_model
    - Add `response_model=UpdateRecordResponse` to decorator
    - _Requirements: 3.1_

- [x] 3. Update RecordService to return Pydantic models
  - [x] 3.1 Import Pydantic models in record_service.py
    - Add imports for `DBConnectionResponse`, `UpdateRecordResponse`, `RecordResponse`, `FileInfo`
    - _Requirements: 4.1_
  - [x] 3.2 Update check_db_connection method
    - Change return type to `DBConnectionResponse`
    - Return `DBConnectionResponse` instances with database name on success
    - _Requirements: 2.2, 2.3_
  - [x] 3.3 Update _process_file method to return FileInfo
    - Change return type to use `FileInfo` model
    - _Requirements: 3.2_
  - [x] 3.4 Update update_record method
    - Change return type to `UpdateRecordResponse`
    - Return `UpdateRecordResponse` instances for success and unchanged cases
    - _Requirements: 3.1, 4.1, 4.3_
