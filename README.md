# FastAPI Record Management Service

A FastAPI application with Google ADK agent integration and MongoDB backend for managing records with file upload capabilities.

## Project Structure

```
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration management (singleton)
├── agents/
│   └── agent.py            # Google ADK agent definition
├── db/
│   ├── connection.py       # MongoDB async connection (Motor)
│   └── schemas.py          # Pydantic models for API validation
├── services/
│   └── record_service.py   # Business logic for record operations
├── utils/
│   └── file_utils.py       # CSV/Excel file processing utilities
└── scripts/
    └── create_schema.py    # MongoDB schema setup script
```

## Setup

### Prerequisites

- Python 3.10+
- MongoDB instance
- Google Cloud project with Vertex AI enabled

### Clone the Repository

```bash
git clone https://github.com/thepratyushranjan/batch-engine.git
cd batch-engine
```

### Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Google Cloud (required)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_APPLICATION_CREDENTIALS=vertex-ai-user.json

# MongoDB (required)
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net
MONGODB_DATABASE=your_database
MONGODB_COLLECTION=collection_name
```

### Database Setup

Initialize MongoDB schema and indexes:

```bash
python scripts/create_schema.py
```

## Running the Server

```bash
python main.py or uv run main.py
```

Server starts at `http://localhost:8000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/db-test` | Test MongoDB connection |
| PATCH | `/records/{id}` | Update record with file uploads |

### Update Record Example

```bash
curl -X PATCH "http://localhost:8000/records/{record_id}" \
  -F "user_input=@data.csv" \
  -F "expected_output=@output.xlsx" \
  -F "instruction_from_user=Process this data" \
  -F "client_email_address=user@example.com"
```

Accepts CSV/Excel files and extracts column metadata for storage.

## MongoDB Document Schema

Example document structure in the collection:

```json
{
  "_id": "ObjectId('69317bf8f33ba37443c3c902')",
  "task_id": "496dcf54-2079-4f8d-b2c9-e0fef1217fbe",
  "user_input": [
    {
      "filename": "Sample Data.xlsx",
      "columns": ["VIN", "Registration Number", "Engine Number"]
    }
  ],
  "expected_output": [
    "VIN",
    "Registration Number",
    "regDate",
    "Model Variant",
    "Registration Validity Date",
    "Colour",
    "Fuel Type",
    "Owner Name",
    "Owner Serial",
    "District",
    "State",
    "City",
    "Pincode",
    "Registration Authority Name",
    "Registration Authority Code",
    "Vehicle Class",
    "Insurance Company Name",
    "Financer Name",
    "Vahan Commercial status",
    "Invincible Intelligence"
  ],
  "instruction_from_user": "Your prompt here",
  "client_email_address": "user@example.com",
  "progress": 0,
  "created_date": "2025-12-04T17:48:00.592+00:00",
  "updated_date": "2025-12-05T11:48:37.035+00:00"
}
```

## Key Components

- **Pydantic Models** (`db/schemas.py`): Type-safe request/response validation with automatic OpenAPI docs
- **RecordService** (`services/record_service.py`): Async record operations with custom exceptions
- **File Utils** (`utils/file_utils.py`): Handles CSV/Excel parsing with multiple encoding support
- **Google ADK Agent** (`agents/agent.py`): Gemini-powered agent (currently configured for time queries)

## API Documentation

Interactive docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
