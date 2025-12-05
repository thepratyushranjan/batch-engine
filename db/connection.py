from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from config import config


class MongoDB:
    client: AsyncIOMotorClient = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        mongodb_url = config.mongodb_url
        cls.client = AsyncIOMotorClient(mongodb_url, server_api=ServerApi("1"))
        print(f"Connected to MongoDB at {mongodb_url}")

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed")

    @classmethod
    def get_database(cls, db_name: str = None):
        """Get database instance"""
        db_name = db_name or config.mongodb_database
        return cls.client[db_name]

    @classmethod
    def get_collection(cls, collection_name: str, db_name: str = None):
        """Get collection instance"""
        db = cls.get_database(db_name)
        return db[collection_name]


mongodb = MongoDB()
