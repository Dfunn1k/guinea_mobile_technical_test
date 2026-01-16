import random
from datetime import datetime

from sqlmodel import Session

from app.db import get_engine
from app.models import Partner

SAMPLE_PARTNERS = [
    {
        "external_id": "ext-1001",
        "name": "Comercial Andina",
        "vat": "20123456789",
        "email": "ventas@andina.pe",
        "phone": "+51 1 555-0101",
        "street": "Av. Los Olivos 123",
        "city": "Lima",
        "country_code": "PE",
    },
    {
        "external_id": "ext-1002",
        "name": "Servicios Amazonia",
        "vat": "10456789123",
        "email": "contacto@amazonia.pe",
        "phone": "+51 1 555-0102",
        "street": "Jr. Amazonas 456",
        "city": "Iquitos",
        "country_code": "PE",
    },
    {
        "external_id": "ext-1003",
        "name": "Insumos Pacifico",
        "vat": "20567891234",
        "email": "ventas@pacifico.pe",
        "phone": "+51 1 555-0103",
        "street": "Av. Grau 789",
        "city": "Trujillo",
        "country_code": "PE",
    },
]


def main() -> None:
    engine = get_engine()
    with Session(engine) as session:
        for partner in SAMPLE_PARTNERS:
            score = round(random.uniform(0.2, 0.95), 2)
            record = Partner(**partner, score=score, updated_at=datetime.utcnow())
            session.add(record)
        session.commit()
    print("Datos poblados correctamente")


if __name__ == "__main__":
    main()
