import os
import pytest
from fastapi.testclient import TestClient

from app.core import config
from app.db import init_db


@pytest.fixture(scope="session", autouse=True)
def _configure_settings():
    os.environ["FASTAPI_DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["FASTAPI_API_TOKEN"] = "test-token"
    os.environ["FASTAPI_LOG_LEVEL"] = "INFO"
    config.get_settings.cache_clear()
    init_db()


@pytest.fixture()
def client():
    from app.main import app

    return TestClient(app)
