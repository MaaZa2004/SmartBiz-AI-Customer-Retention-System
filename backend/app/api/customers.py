from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

from app.core.db import get_db
from app.core.auth import require_authenticated, require_manager
from app.models.models import Customer, Sale, Transaction, Prediction, Recommendation
from app.schemas.schemas import CustomerResponse, CustomerBase

router = APIRouter(prefix="/customers", tags=["Customer Management"])

@router.get("/", response_model=List[CustomerResponse])
def list_customers(
    skip: int = 0,
    limit: int = 100,
    product_category: Optional[str] = None,
    churn_only: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_authenticated)
):
    """Lists customer profiles, with optional filtering by product category and churn status."""
    query = db.query(Customer)
    if product_category:
        query = query.filter(Customer.product_category == product_category)
    if churn_only is not None:
        query = query.filter(Customer.churn == (1 if churn_only else 0))
        
    return query.offset(skip).limit(limit).all()

@router.get("/{customer_id}", response_model=dict)
def get_customer_details(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_authenticated)
):
    """Retrieves full details of a specific customer, including prediction history and recommendations."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found."
        )
        
    from app.schemas.schemas import PredictionResponse, RecommendationResponse, SaleResponse
    
    predictions = db.query(Prediction).filter(Prediction.customer_id == customer_id).order_by(Prediction.created_at.desc()).all()
    recommendations = db.query(Recommendation).filter(Recommendation.customer_id == customer_id).order_by(Recommendation.created_at.desc()).all()
    sales = db.query(Sale).filter(Sale.customer_id == customer_id).all()
    
    return {
        "customer": CustomerResponse.model_validate(customer),
        "predictions": [PredictionResponse.model_validate(p) for p in predictions],
        "recommendations": [RecommendationResponse.model_validate(r) for r in recommendations],
        "sales": [SaleResponse.model_validate(s) for s in sales]
    }

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_in: CustomerBase,
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)
):
    """Manually inserts a new customer profile. Restricted to Manager/Admin roles."""
    existing = db.query(Customer).filter(Customer.id == customer_in.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with ID {customer_in.id} already exists."
        )
        
    db_customer = Customer(**customer_in.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.post("/seed", status_code=status.HTTP_200_OK)
def seed_db_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)
):
    """
    Clears existing customer/sales/transaction tables and seeds them with 
    records loaded directly from the real Kaggle customer churn dataset.
    """
    from app.core.seed import seed_database
    try:
        seed_database()
        return {
            "status": "success",
            "message": "Successfully seeded database using the real Kaggle customer churn dataset."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database seeding failed: {str(e)}"
        )
