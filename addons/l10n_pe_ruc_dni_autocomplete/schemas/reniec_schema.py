from dataclasses import dataclass


@dataclass(frozen=True)
class ReniecDTO:
    first_name: str | None = None
    first_last_name: str | None = None
    second_last_name: str | None = None
    full_name: str | None = None
    document_number: str | None = None

    @staticmethod
    def from_payload(payload: dict[str, str]):
        return ReniecDTO(
            first_name=payload.get('first_name'),
            first_last_name=payload.get('first_last_name'),
            second_last_name=payload.get('second_last_name'),
            full_name=payload.get('full_name'),
            document_number=payload.get('document_number')
        )

    