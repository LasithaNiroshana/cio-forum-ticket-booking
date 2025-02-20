from motor.motor_asyncio import AsyncIOMotorClient
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str

    class Config:
        env_file = ".cfg"
        env_file_encoding = "utf-8"


settings = Settings()

# Create a MongoDB client
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client["ticket-booking"]  # Use your database name


# Dependency to get the database connection
async def get_db():
    return db
