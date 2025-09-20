from pydantic import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    mongo_connection_string: str
    db_name: str = "property_maintenance_db"

    # Auth0
    auth0_domain: str
    auth0_api_audience: str
    auth0_algorithms: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
