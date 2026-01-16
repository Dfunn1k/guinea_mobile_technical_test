from app.services.normalization import normalize_partner_data


def test_normalize_partner_data():
    payload = {
        "name": "  ACME  SAC  ",
        "email": " INFO@ACME.PE ",
        "phone": " 999 888 777 ",
        "street": "  Av. Siempre Viva  ",
        "city": " Lima ",
        "country_code": " pe ",
    }

    normalized = normalize_partner_data(payload)

    assert normalized["name"] == "ACME SAC"
    assert normalized["email"] == "info@acme.pe"
    assert normalized["phone"] == "999 888 777"
    assert normalized["street"] == "Av. Siempre Viva"
    assert normalized["city"] == "Lima"
    assert normalized["country_code"] == "pe"
