import uvicorn
from fastapi import FastAPI
from pydantic.v1 import BaseSettings
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from routers.booking_router import bookingRouter
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    MONGODB_URL: str

    class Config:
        env_file = ".cfg"
        env_file_encoding = "utf-8"


settings = Settings()

app = FastAPI()


# Connect to MongoDB
@app.on_event("startup")
async def startup_db_client():
    try:
        app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        app.mongodb = app.mongodb_client["ticket-booking"]  # Use your database name
        logger.info("Connected to MongoDB.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        app.mongodb_client.close()
        logger.info("MongoDB connection closed.")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/public", StaticFiles(directory="public"), name="public")

app.include_router(bookingRouter)


if __name__ == '__main__':
    uvicorn.run(app, port=8000, host="0.0.0.0")

# SystemRouter.update_routes(routes=app.routes)
