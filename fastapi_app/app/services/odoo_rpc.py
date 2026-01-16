import logging
from datetime import datetime
from typing import Any

import httpx
from sqlmodel import Session, select

from ..core.config import get_settings
from ..models import Partner

_logger = logging.getLogger(__name__)


def _jsonrpc_call(
    client: httpx.Client,
    url: str,
    service: str,
    method: str,
    args: list[Any],
    request_id: str,
) -> Any:
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": service,
            "method": method,
            "args": args,
        },
        "id": request_id,
    }
    response = client.post(url, json=payload)
    response.raise_for_status()
    body = response.json()
    if "error" in body:
        raise RuntimeError(body["error"].get("message", "Unknown JSON-RPC error"))
    return body.get("result")


def _authenticate(client: httpx.Client, url: str, db: str, username: str, password: str) -> int:
    uid = _jsonrpc_call(
        client,
        url,
        "common",
        "login",
        [db, username, password],
        request_id="auth",
    )
    if not uid:
        raise RuntimeError("No se pudo autenticar contra Odoo.")
    return uid


def _resolve_country_ids(client: httpx.Client, url: str, db: str, uid: int, password: str, codes: set[str]) -> dict[str, int]:
    if not codes:
        return {}
    records = _jsonrpc_call(
        client,
        url,
        "object",
        "execute_kw",
        [
            db,
            uid,
            password,
            "res.country",
            "search_read",
            [[["code", "in", sorted(codes)]]],
            {"fields": ["code", "id"]},
        ],
        request_id="countries",
    )
    return {record["code"]: record["id"] for record in records or []}


def _resolve_identification_type_ids(
    client: httpx.Client, url: str, db: str, uid: int, password: str, codes: set[str]
) -> dict[str, int]:
    if not codes:
        return {}
    normalized_codes = {code.strip().upper() for code in codes if code}
    records = _jsonrpc_call(
        client,
        url,
        "object",
        "execute_kw",
        [
            db,
            uid,
            password,
            "l10n_latam.identification.type",
            "search_read",
            [[["code", "in", sorted(normalized_codes)]]],
            {"fields": ["code", "id"]},
        ],
        request_id="identification-types",
    )
    return {record["code"].upper(): record["id"] for record in records or []}


def _build_partner_payload(
    partner: Partner,
    country_map: dict[str, int],
    identification_type_map: dict[str, int],
) -> dict[str, Any]:
    values: dict[str, Any] = {
        "external_id": partner.external_id,
        "name": partner.name,
        "vat": partner.vat,
        "email": partner.email,
        "phone": partner.phone,
        "street": partner.street,
        "city": partner.city,
        "company_type": partner.company_type,
        "type": partner.contact_type,
        "external_score": partner.score,
        "external_updated_at": partner.updated_at.isoformat() if partner.updated_at else None,
        "external_last_sync_at": datetime.utcnow().isoformat(),
    }
    if partner.country_code and partner.country_code in country_map:
        values["country_id"] = country_map[partner.country_code]
    if partner.identification_type_code:
        identification_code = partner.identification_type_code.strip().upper()
        if identification_code in identification_type_map:
            values["l10n_latam_identification_type_id"] = identification_type_map[identification_code]
    return {key: value for key, value in values.items() if value is not None}


def sync_partners_to_odoo(session: Session) -> dict[str, int]:
    settings = get_settings()
    partners = session.exec(select(Partner)).all()
    if not partners:
        return {"created": 0, "updated": 0, "total": 0}

    url = f"{settings.odoo_url.rstrip('/')}/jsonrpc"
    with httpx.Client(timeout=settings.odoo_timeout) as client:
        uid = _authenticate(client, url, settings.odoo_db, settings.odoo_username, settings.odoo_password)
        country_codes = {partner.country_code for partner in partners if partner.country_code}
        country_map = _resolve_country_ids(client, url, settings.odoo_db, uid, settings.odoo_password, country_codes)
        identification_codes = {partner.identification_type_code for partner in partners if partner.identification_type_code}
        identification_type_map = _resolve_identification_type_ids(
            client, url, settings.odoo_db, uid, settings.odoo_password, identification_codes
        )

        external_ids = [partner.external_id for partner in partners]
        existing = _jsonrpc_call(
            client,
            url,
            "object",
            "execute_kw",
            [
                settings.odoo_db,
                uid,
                settings.odoo_password,
                "res.partner",
                "search_read",
                [[["external_id", "in", external_ids]]],
                {"fields": ["id", "external_id"]},
            ],
            request_id="existing",
        )
        existing_map = {record["external_id"]: record["id"] for record in existing or []}

        created = 0
        updated = 0
        for partner in partners:
            payload = _build_partner_payload(partner, country_map, identification_type_map)
            existing_id = existing_map.get(partner.external_id)
            if existing_id:
                _jsonrpc_call(
                    client,
                    url,
                    "object",
                    "execute_kw",
                    [
                        settings.odoo_db,
                        uid,
                        settings.odoo_password,
                        "res.partner",
                        "write",
                        [[existing_id], payload],
                    ],
                    request_id=f"write-{partner.external_id}",
                )
                updated += 1
            else:
                _jsonrpc_call(
                    client,
                    url,
                    "object",
                    "execute_kw",
                    [
                        settings.odoo_db,
                        uid,
                        settings.odoo_password,
                        "res.partner",
                        "create",
                        [[payload]],
                    ],
                    request_id=f"create-{partner.external_id}",
                )
                created += 1

    _logger.info("odoo_bulk_sync completed created=%s updated=%s", created, updated)
    return {"created": created, "updated": updated, "total": len(partners)}
