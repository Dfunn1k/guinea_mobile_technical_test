from typing import Optional


def normalize_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = " ".join(value.strip().split())
    return cleaned or None


def normalize_email(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value.strip().lower() or None


def normalize_partner_data(payload: dict) -> dict:
    return {
        **payload,
        "name": normalize_text(payload.get("name")),
        "vat": normalize_text(payload.get("vat")),
        "email": normalize_email(payload.get("email")),
        "phone": normalize_text(payload.get("phone")),
        "street": normalize_text(payload.get("street")),
        "city": normalize_text(payload.get("city")),
        "country_code": normalize_text(payload.get("country_code")),
    }
