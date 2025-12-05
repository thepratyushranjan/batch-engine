"""MongoDB Schema Creation Script with JSON Schema validation"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
import uuid

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from pymongo.errors import CollectionInvalid
from config import config


SCHEMAS = {
    "test_collection": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["task_id", "created_date"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "task_id": {"bsonType": "string"},
                    "user_input": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["filename", "columns"],
                            "properties": {
                                "filename": {"bsonType": "string"},
                                "columns": {"bsonType": "array", "items": {"bsonType": "string"}}
                            }
                        }
                    },
                    "expected_output": {"bsonType": "array", "items": {"bsonType": "string"}},
                    "instruction_from_user": {"bsonType": "string"},
                    "client_email_address": {"bsonType": "string"},
                    "progress": {"bsonType": ["int", "double"], "minimum": 0, "maximum": 100},
                    "created_date": {"bsonType": "date"},
                    "updated_date": {"bsonType": "date"},
                    "error_message": {"bsonType": "string"}
                }
            }
        },
        "validationLevel": "moderate",
        "validationAction": "error"
    }
}

INDEXES = {
       "test_collection": [
           {"keys": [("task_id", 1)], "options": {"unique": True}},
           {"keys": [("created_date", -1)]},
           {"keys": [("client_email_address", 1)]}
       ]
   }


async def setup_collection(db, name, schema, drop=False):
    """Create or update collection with schema"""
    if drop and name in await db.list_collection_names():
        await db.drop_collection(name)
        print(f"✗ Dropped '{name}'")
    
    try:
        await db.create_collection(name, **schema)
        print(f"✓ Created '{name}'")
    except CollectionInvalid:
        await db.command({"collMod": name, **schema})
        print(f"✓ Updated '{name}'")


async def setup_indexes(db, name, indexes):
    """Create indexes for collection"""
    collection = db[name]
    for idx in indexes:
        await collection.create_index(idx["keys"], **idx.get("options", {}))
        print(f"  → Index on {idx['keys']}")


async def verify_schema(db, name):
    """Verify and display schema validation"""
    info = await db.command("listCollections", filter={"name": name})
    if batch := info["cursor"]["firstBatch"]:
        validator = batch[0].get("options", {}).get("validator", {})
        if validator:
            required = validator.get('$jsonSchema', {}).get('required', [])
            print(f"✓ '{name}' validation - Required: {required or 'None'}")


async def insert_sample(db, name):
    """Insert sample document"""
    # Get current IST time and convert to naive datetime for MongoDB
    ist_now = datetime.now(IST)
    now = ist_now.replace(tzinfo=None)
    doc = {
        "task_id": str(uuid.uuid4()),
        "user_input": [{"filename": "Sample_Data.xlsx", "columns": ["VIN", "Reg_No", "Engine_No"]}],
        "expected_output": ["result", "status", "timestamp"],
        "instruction_from_user": "Process vehicle data",
        "client_email_address": "test@example.com",
        "progress": 0,
        "created_date": now,
        "updated_date": now
    }
    result = await db[name].insert_one(doc)
    print(f"✓ Sample inserted: {result.inserted_id}")
    
    doc = await db[name].find_one({"_id": result.inserted_id})
    print(f"  Task: {doc['task_id'][:8]}... | Progress: {doc['progress']}% | Files: {len(doc['user_input'])}")


async def main():
    """Main execution"""
    if not config.mongodb_url:
        print("✗ MONGODB_URL not configured")
        return
    
    print(f"→ Connecting to {config.mongodb_database}...")
    client = AsyncIOMotorClient(config.mongodb_url, server_api=ServerApi("1"))
    
    try:
        await client.admin.command('ping')
        print("✓ Connected\n")
        
        db = client[config.mongodb_database]
        DROP_EXISTING = False
        
        for name, schema in SCHEMAS.items():
            await setup_collection(db, name, schema, DROP_EXISTING)
            if name in INDEXES:
                await setup_indexes(db, name, INDEXES[name])
        
        print(f"\n{'─' * 50}")
        for name in SCHEMAS:
            await verify_schema(db, name)
        
        print(f"\n{'─' * 50}")
        await insert_sample(db, "test_collection")
        
        collections = await db.list_collection_names()
        print(f"\n✓ Complete. Collections: {collections}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())