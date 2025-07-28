from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Loads environment variables from the .env file."""
    GOOGLE_API_KEY: str
    MONGO_DB_URL: str
    DB_NAME: str

    # --- ADD THESE TWO LINES ---
    QDRANT_URL: str
    QDRANT_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()