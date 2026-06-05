import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables from .env file
load_dotenv()

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "my_db")

# Global MongoDB client and database instances (initialized at startup)
mongodb_client: AsyncIOMotorClient = None
mongodb_db = None


async def connect_to_mongodb():
    global mongodb_client, mongodb_db

    if mongodb_client is not None:
        print("MongoDB connection already established.")
        return

    mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    mongodb_db = mongodb_client[MONGODB_DB_NAME]

    # Test connection
    await mongodb_client.admin.command('ping')
    print(f"Connected to MongoDB: {MONGODB_DB_NAME}")


async def close_mongodb_connection():
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("✅ Closed MongoDB connection")


def get_mongodb():
    return mongodb_db
