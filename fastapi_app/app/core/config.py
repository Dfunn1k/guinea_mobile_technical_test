from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://fastapi:fastapi@fastapi_db:5432/fastapi"
    api_token: str = "change-me"
    log_level: str = "INFO"
    odoo_url: str = "http://odoo:8069"
    odoo_db: str = "odoo"
    odoo_username: str = "admin"
    odoo_password: str = "admin"
    odoo_timeout: float = 10.0

    class Config:
        env_prefix = "FASTAPI_"


@lru_cache
def get_settings() -> Settings:
    return Settings()
