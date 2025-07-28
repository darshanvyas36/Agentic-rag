from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Loads environment variables from the .env file."""
    GOOGLE_API_KEY: str
    MONGO_DB_URL: str
    DB_NAME: str

    class Config:
        env_file = ".env"

# Create a single instance of the settings to be used throughout the app
settings = Settings()