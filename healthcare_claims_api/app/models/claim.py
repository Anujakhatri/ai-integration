from sqlalchemy import Column, Integer, String, Float, DateTime, Date, func
from app.db.database import Base
from pydantic import BaseModel, validator
from datetime import date
import re

# 1. SQLAlchemy Model = PostgreSQL Table
class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String, nullable=False)
    icd10_code = Column(String, nullable=False)
    cpt_code = Column(String, nullable=False)
    paid_amount = Column(Float, nullable=False)
    date_of_service = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())


class ClaimSchema(BaseModel):

    member_id : str
    icd10_code : str
    cpt_code : str
    paid_amount : float
    date_of_service : date

    # ICD-10 format validate garchha: J18.9, A01, B02.1234
    @validator('icd10_code')
    def validate_icd10_code(cls, v):
        pattern = r"^[A-Z]\d{2}\.?\d{0,4}$"
        if not re.match(pattern, v):
            raise ValueError(f"Invalid ICD10 code:{v}")
        return v

    # Future date reject garchha
    @validator('date_of_service')
    def validate_date_of_service(cls, v):
        if v > date.today():
            raise ValueError(f"date of service cannot be in future:{v}")
        return v

    class Config:
        from_attributes = True