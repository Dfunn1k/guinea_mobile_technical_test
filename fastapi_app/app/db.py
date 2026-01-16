from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine

from .core.config import get_settings


def get_engine():
    settings = get_settings()
    return create_engine(settings.database_url, echo=False, pool_pre_ping=True)


def init_db() -> None:
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    engine = get_engine()
    with Session(engine) as session:
        yield session
