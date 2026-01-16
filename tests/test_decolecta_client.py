import importlib.util
import sys
from types import ModuleType
from pathlib import Path

_MODULE_PATH = Path(__file__).resolve().parents[1] / "addons" / "l10n_pe_ruc_dni_autocomplete" / "services" / "decolecta_client.py"
package_name = "addons.l10n_pe_ruc_dni_autocomplete.services"
base_path = Path(__file__).resolve().parents[1] / "addons" / "l10n_pe_ruc_dni_autocomplete" / "services"
for name in ["addons", "addons.l10n_pe_ruc_dni_autocomplete", package_name]:
    if name not in sys.modules:
        module = ModuleType(name)
        module.__path__ = [str(base_path)]
        sys.modules[name] = module

spec = importlib.util.spec_from_file_location(f"{package_name}.decolecta_client", _MODULE_PATH)
decolecta_client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decolecta_client)

fetch_decolecta_payload = decolecta_client.fetch_decolecta_payload


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_fetch_decolecta_payload(monkeypatch):
    def fake_request(method, url, headers=None, params=None, timeout=None, json=None, data=None):
        assert method == "GET"
        assert "sunat" in url
        assert headers["Authorization"].startswith("Bearer")
        return DummyResponse({"numero_documento": "20123456789"})

    monkeypatch.setattr(
        "addons.l10n_pe_ruc_dni_autocomplete.services.http_client.requests.request",
        fake_request,
    )
    payload = fetch_decolecta_payload(
        base_url="https://api.decolecta.com/v1",
        token="token",
        endpoint="sunat/ruc/full",
        params={"numero": "20123456789"},
    )
    assert payload["numero_documento"] == "20123456789"
