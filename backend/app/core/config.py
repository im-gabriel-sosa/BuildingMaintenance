from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    MONGO_CONNECTION_STRING: str
    DB_NAME: str = "property_maintenance_db"

    # Auth0
    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ALGORITHMS: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
