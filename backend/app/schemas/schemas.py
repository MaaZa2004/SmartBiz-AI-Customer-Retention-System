from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# --- AUTHENTICATION SCHEMAS ---

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: str = Field(..., description="Admin, Business Analyst, or Manager")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None

# --- CUSTOMER SCHEMAS ---

class CustomerBase(BaseModel):
    id: str
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    tenure: Optional[int] = None
    satisfaction_score: Optional[int] = None
    num_orders: Optional[int] = None
    total_spending: Decimal = Decimal("0.00")
    last_purchase_date: Optional[date] = None
    product_category: Optional[str] = None
    
    warehouse_to_home: Optional[int] = None
    marital_status: Optional[str] = None
    num_addresses: Optional[int] = None
    num_devices_registered: Optional[int] = None
    days_since_last_order: Optional[int] = None
    cashback_amount: Decimal = Decimal("0.00")
    complain: int = 0
    churn: int = 0

class CustomerResponse(CustomerBase):
    created_at: datetime

    class Config:
        from_attributes = True

# --- SALES SCHEMAS ---

class SaleBase(BaseModel):
    customer_id: str
    date: date
    amount: Decimal
    product_category: Optional[str] = None

class SaleResponse(SaleBase):
    id: int

    class Config:
        from_attributes = True

# --- TRANSACTION SCHEMAS ---

class TransactionBase(BaseModel):
    customer_id: str
    sale_id: Optional[int] = None
    amount: Decimal
    status: str

class TransactionResponse(TransactionBase):
    id: int
    transaction_date: datetime

    class Config:
        from_attributes = True

# --- ML PREDICTION SCHEMAS ---

class PredictionCreate(BaseModel):
    customer_id: str
    model_type: str  # 'churn', 'segment', 'forecast'
    result_value: str
    confidence_score: Optional[float] = None

class PredictionResponse(PredictionCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- RECOMMENDATION SCHEMAS ---

class RecommendationCreate(BaseModel):
    customer_id: str
    recommendation_text: str
    action_type: str  # 'retention action', 'marketing suggestion', 'next-best-action'
    priority: str  # 'High', 'Medium', 'Low'

class RecommendationResponse(RecommendationCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- ML ENDPOINT REQUESTS/RESPONSES ---

class ChurnPredictRequest(BaseModel):
    customer_id: str

class ChurnPredictResponse(BaseModel):
    customer_id: str
    churn_probability: float
    risk_level: str  # 'Low', 'Medium', 'High'

class SegmentPredictRequest(BaseModel):
    customer_id: str

class SegmentPredictResponse(BaseModel):
    customer_id: str
    segment: str  # 'Premium', 'Regular', 'Low-Value'
    details: dict

class ForecastPredictRequest(BaseModel):
    product_category: str
    forecast_days: int = 30

class ForecastPredictResponse(BaseModel):
    product_category: str
    expected_sales_value: float
    trend_direction: str  # 'Upward', 'Downward', 'Stable'

class DecisionEngineRequest(BaseModel):
    customer_id: str

class DashboardKPIs(BaseModel):
    total_revenue: float
    active_customers: int
    churn_rate: float
    forecasted_sales: float
