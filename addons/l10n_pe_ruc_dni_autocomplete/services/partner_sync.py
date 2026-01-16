import json
from datetime import datetime
from typing import Any


def log_event(logger, event: str, **fields: Any) -> None:
    payload = {
        "event": event,
        "timestamp": datetime.utcnow().isoformat(),
        **fields,
    }
    logger.info(json.dumps(payload, ensure_ascii=False, default=str))


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.strip().split())
    return cleaned or None


def normalize_email(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().lower() or None


def build_external_payload(partner) -> dict[str, Any]:
    external_id = partner.external_id or f"odoo-{partner.id}"
    return {
        "external_id": external_id,
        "name": normalize_text(partner.name),
        "vat": normalize_text(partner.vat),
        "email": normalize_email(partner.email),
        "phone": normalize_text(partner.phone),
        "street": normalize_text(partner.street),
        "city": normalize_text(partner.city),
        "country_code": normalize_text(partner.country_id.code if partner.country_id else None),
        "score": partner.external_score,
        "updated_at": datetime.utcnow().isoformat(),
    }


def reconcile_partner_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not payload:
        return {}
    values = {
        "external_id": payload.get("external_id"),
        "external_score": payload.get("score"),
        "external_updated_at": payload.get("updated_at"),
        "external_last_sync_at": datetime.utcnow(),
    }
    return {key: value for key, value in values.items() if value is not None}
