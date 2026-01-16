from datetime import datetime, timedelta

from app.services.reconciliation import should_accept_update


def test_should_accept_update_newer():
    existing = datetime.utcnow()
    incoming = existing + timedelta(minutes=5)
    assert should_accept_update(existing, incoming)


def test_should_reject_older_update():
    existing = datetime.utcnow()
    incoming = existing - timedelta(minutes=5)
    assert not should_accept_update(existing, incoming)
