from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class PartnerBase(SQLModel):
    external_id: str = Field(index=True, nullable=False)
    name: Optional[str] = None
    vat: Optional[str] = None
    identification_type_code: Optional[str] = None
    company_type: Optional[str] = None
    contact_type: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    country_code: Optional[str] = None
    score: float = 0.0
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Partner(PartnerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PartnerCreate(PartnerBase):
    pass


class PartnerRead(PartnerBase):
    id: int
    created_at: datetime


class PartnerUpdate(SQLModel):
    name: Optional[str] = None
    vat: Optional[str] = None
    identification_type_code: Optional[str] = None
    company_type: Optional[str] = None
    contact_type: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    country_code: Optional[str] = None
    score: Optional[float] = None
    updated_at: Optional[datetime] = None
