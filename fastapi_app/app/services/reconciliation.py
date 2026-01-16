from datetime import datetime
from typing import Optional


class ConflictError(Exception):
    pass


def parse_datetime(value: str | None) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


def should_accept_update(existing_updated_at: datetime, incoming_updated_at: Optional[datetime]) -> bool:
    if incoming_updated_at is None:
        return True
    return incoming_updated_at >= existing_updated_at
