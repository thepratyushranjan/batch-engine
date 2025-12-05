# Design Document

## Overview

This design outlines how to integrate the existing Pydantic models from `schemas.py` into the FastAPI endpoints and service layer. The goal is to leverage FastAPI's native Pydantic support for automatic validation, serialization, and OpenAPI documentation generation.

## Architecture

The integration follows a layered approach:

```
┌─────────────────────────────────────────────────────┐
│                    FastAPI Endpoints                │
│         (response_model=PydanticModel)              │
├─────────────────────────────────────────────────────┤
│                    Service Layer                    │
│         (returns Pydantic model instances)          │
├─────────────────────────────────────────────────────┤
│                    Data Layer                       │
│         (MongoDB documents → Pydantic models)       │
└─────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Updated Pydantic Models (`schemas.py`)

Add new response models to support all endpoint responses:

```python
class UpdateRecordResponse(BaseModel):
    """Response schema for record update operations"""
    status: str
    message: str
    data: Optional[RecordResponse] = None

class ErrorResponse(BaseModel):
    """Standard error response schema"""
    detail: str
```

### 2. FastAPI Endpoints (`main.py`)

Update endpoints to use `response_model` parameter:

```python
@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="healthy", message="Server is running")

@app.get("/db-test", response_model=DBConnectionResponse)
async def test_db() -> DBConnectionResponse:
    return await record_service.check_db_connection()

@app.patch("/records/{id}", response_model=UpdateRecordResponse)
async def update_record_with_csv(...) -> UpdateRecordResponse:
    ...
```

### 3. Service Layer (`services/record_service.py`)

Update service methods to return Pydantic models:

```python
async def check_db_connection(self) -> DBConnectionResponse:
    """Returns DBConnectionResponse instead of dict"""
    ...

async def update_record(...) -> UpdateRecordResponse:
    """Returns UpdateRecordResponse instead of dict"""
    ...
```

## Data Models

### Existing Models (no changes needed)

| Model | Purpose |
|-------|---------|
| `FileInfo` | File metadata with filename and columns |
| `RecordUpdateForm` | Form fields for PATCH request |
| `RecordResponse` | Full record data structure |
| `HealthResponse` | Health check response |
| `DBConnectionResponse` | DB connection test response |

### New Models to Add

| Model | Purpose |
|-------|---------|
| `UpdateRecordResponse` | Wrapper for record update operation result |

## Error Handling

FastAPI automatically handles Pydantic validation errors and returns 422 responses. The existing HTTPException handling in `main.py` remains unchanged for business logic errors (400, 404).

## Testing Strategy

1. Verify endpoints return correct response structure
2. Confirm OpenAPI docs show proper schemas
3. Test that invalid data triggers Pydantic validation errors
4. Ensure MongoDB document to Pydantic model conversion works correctly
