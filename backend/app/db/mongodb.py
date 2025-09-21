from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Global variables for the MongoDB client and database
client = None
db = None

async def connect_to_mongo():
    """
    Connects to the MongoDB Atlas database.
    """
    global client, db
    print("Connecting to MongoDB...")
    try:
        client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)
        db = client[settings.DB_NAME]
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

async def close_mongo_connection():
    """
    Closes the MongoDB connection.
    """
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")

def get_db():
    """
    FastAPI dependency to get the database instance.
    """
    return db
