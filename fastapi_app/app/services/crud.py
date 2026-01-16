import logging
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from ..models import Partner, PartnerCreate, PartnerUpdate
from .normalization import normalize_partner_data
from .reconciliation import ConflictError, should_accept_update

_logger = logging.getLogger(__name__)


def get_partner_by_external_id(session: Session, external_id: str) -> Optional[Partner]:
    statement = select(Partner).where(Partner.external_id == external_id)
    return session.exec(statement).first()


def create_partner(session: Session, payload: PartnerCreate) -> Partner:
    normalized = normalize_partner_data(payload.dict())
    partner = Partner(**normalized)
    session.add(partner)
    session.commit()
    session.refresh(partner)
    _logger.info("partner_created external_id=%s", partner.external_id)
    return partner


def upsert_partner(session: Session, payload: PartnerCreate) -> Partner:
    existing = get_partner_by_external_id(session, payload.external_id)
    if not existing:
        return create_partner(session, payload)

    incoming_updated = payload.updated_at
    if not should_accept_update(existing.updated_at, incoming_updated):
        raise ConflictError("Incoming update is older than existing record")

    update_data = normalize_partner_data(payload.dict())
    for key, value in update_data.items():
        setattr(existing, key, value)
    existing.updated_at = incoming_updated or datetime.utcnow()
    session.add(existing)
    session.commit()
    session.refresh(existing)
    _logger.info("partner_updated external_id=%s", existing.external_id)
    return existing


def update_partner(session: Session, partner: Partner, payload: PartnerUpdate) -> Partner:
    update_data = normalize_partner_data(payload.dict(exclude_unset=True))
    incoming_updated = payload.updated_at
    if incoming_updated and not should_accept_update(partner.updated_at, incoming_updated):
        raise ConflictError("Incoming update is older than existing record")
    for key, value in update_data.items():
        setattr(partner, key, value)
    partner.updated_at = incoming_updated or datetime.utcnow()
    session.add(partner)
    session.commit()
    session.refresh(partner)
    _logger.info("partner_updated external_id=%s", partner.external_id)
    return partner
