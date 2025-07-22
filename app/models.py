from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Commitment(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    category: str = Field(default="Other")

class FinancialInput(BaseModel):
    monthly_commitments: List[Commitment]
    current_savings: float = Field(..., ge=0)
    gross_monthly_salary: float = Field(..., gt=0)
    projection_months: int = Field(..., ge=1, le=360)
    tax_rate: float = Field(default=0.25, ge=0, le=0.5)
    inflation_rate: float = Field(default=0.03, ge=0, le=0.15)
    savings_interest_rate: float = Field(default=0.05, ge=0, le=0.20)

class MonthlyProjection(BaseModel):
    month: int
    year: int
    date: str
    gross_salary: float
    net_salary: float
    total_commitments: float
    monthly_savings: float
    total_savings: float
    commitment_breakdown: List[Dict[str, Any]]

class ProjectionResponse(BaseModel):
    summary: Dict[str, Any]
    monthly_projections: List[MonthlyProjection]
    monthly_summary: List[Dict[str, Any]]