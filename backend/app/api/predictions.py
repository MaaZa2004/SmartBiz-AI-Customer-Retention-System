from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth import require_authenticated, require_analyst
from app.models.models import Customer, Prediction
from app.schemas.schemas import (
    ChurnPredictRequest, ChurnPredictResponse,
    SegmentPredictRequest, SegmentPredictResponse,
    ForecastPredictRequest, ForecastPredictResponse
)
from app.services.ml_services import ml_service

router = APIRouter(prefix="/predict", tags=["Machine Learning Predictions"])

@router.post("/churn", response_model=ChurnPredictResponse)
def predict_churn(
    payload: ChurnPredictRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_authenticated)
):
    """Predicts customer churn probability and risk level (Low, Medium, High). Logged in DB."""
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {payload.customer_id} not found."
        )
        
    try:
        res = ml_service.predict_customer_churn(customer)
        
        # Log to Predictions table
        db_pred = Prediction(
            customer_id=payload.customer_id,
            model_type="churn",
            result_value=f"{res.churn_probability:.4f} ({res.risk_level})",
            confidence_score=res.churn_probability
        )
        db.add(db_pred)
        
        # Update customer churn indicator
        customer.churn = 1 if res.risk_level == "High" else 0
        db.commit()
        
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Churn prediction failed: {str(e)}"
        )

@router.post("/segment", response_model=SegmentPredictResponse)
def predict_segment(
    payload: SegmentPredictRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_authenticated)
):
    """Segments customer into Premium, Regular, or Low-Value based on Tenure, Orders, and Spending."""
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {payload.customer_id} not found."
        )
        
    try:
        res = ml_service.predict_customer_segment(customer)
        
        # Log to Predictions table
        db_pred = Prediction(
            customer_id=payload.customer_id,
            model_type="segment",
            result_value=res.segment,
            confidence_score=1.0
        )
        db.add(db_pred)
        db.commit()
        
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Customer segmentation failed: {str(e)}"
        )

@router.post("/forecast", response_model=ForecastPredictResponse)
def predict_forecast(
    payload: ForecastPredictRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_analyst)
):
    """Forecasts expected category-level sales value and computes trend direction."""
    try:
        res = ml_service.predict_sales_forecast(payload.product_category, db, payload.forecast_days)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sales forecasting failed: {str(e)}"
        )
