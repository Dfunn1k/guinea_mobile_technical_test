import importlib.util
from pathlib import Path

_MODULE_PATH = Path(__file__).resolve().parents[1] / "addons" / "l10n_pe_ruc_dni_autocomplete" / "services" / "partner_sync.py"
spec = importlib.util.spec_from_file_location("partner_sync", _MODULE_PATH)
partner_sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(partner_sync)

build_external_payload = partner_sync.build_external_payload
normalize_email = partner_sync.normalize_email
normalize_text = partner_sync.normalize_text
reconcile_partner_payload = partner_sync.reconcile_partner_payload


class DummyPartner:
    def __init__(self):
        self.id = 42
        self.external_id = None
        self.name = "  Empresa  SAC  "
        self.vat = "  20123456789  "
        self.email = " INFO@EMPRESA.PE "
        self.phone = " 999 888 777 "
        self.street = " Av. Siempre Viva 123 "
        self.city = " Lima "
        self.country_id = type("Country", (), {"code": "PE"})
        self.external_score = 0.75


def test_normalize_helpers():
    assert normalize_text("  hola   mundo ") == "hola mundo"
    assert normalize_text("   ") is None
    assert normalize_email(" TEST@MAIL.COM ") == "test@mail.com"


def test_build_external_payload():
    partner = DummyPartner()
    payload = build_external_payload(partner)
    assert payload["external_id"] == "odoo-42"
    assert payload["name"] == "Empresa SAC"
    assert payload["email"] == "info@empresa.pe"


def test_reconcile_partner_payload():
    payload = {
        "external_id": "ext-999",
        "score": 0.9,
        "updated_at": "2024-01-01T00:00:00",
    }
    values = reconcile_partner_payload(payload)
    assert values["external_id"] == "ext-999"
    assert values["external_score"] == 0.9
