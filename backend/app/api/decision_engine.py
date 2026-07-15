from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth import require_authenticated
from app.schemas.schemas import DecisionEngineRequest, RecommendationResponse
from app.services.decision_engine import decision_engine

router = APIRouter(prefix="/decision-engine", tags=["Decision Engine"])

@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendation(
    payload: DecisionEngineRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_authenticated)
):
    """
    Executes the Decision Engine pipeline for a specific customer.
    Runs predictions (churn, segment, forecast), combines outputs using business logic, 
    persists logs, and returns a tailored recommendation.
    """
    try:
        rec = decision_engine.run_for_customer(db, payload.customer_id)
        return rec
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decision Engine execution failed: {str(e)}"
        )
