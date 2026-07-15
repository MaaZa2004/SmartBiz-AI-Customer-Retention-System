import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.models import Customer, Sale
from app.services.decision_engine import decision_engine
from app.services.ml_services import ml_service

# Define test SQLite DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_ml_decision.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Insert mock customer for testing predictions and decisions
    test_customer = Customer(
        id="C-99999",
        name="Test User",
        gender="Female",
        age=40,
        tenure=24,
        satisfaction_score=4,
        num_orders=15,
        total_spending=Decimal("1500.00"),
        product_category="Laptop & Accessory",
        warehouse_to_home=5,
        marital_status="Married",
        num_addresses=2,
        num_devices_registered=3,
        days_since_last_order=10,
        cashback_amount=Decimal("150.00"),
        complain=0,
        churn=0
    )
    db.add(test_customer)
    
    # Insert mock sales for forecast calculations
    db.add(Sale(customer_id="C-99999", date=pytest.importorskip("datetime").date.today(), amount=Decimal("500.00"), product_category="Laptop & Accessory"))
    db.add(Sale(customer_id="C-99999", date=pytest.importorskip("datetime").date.today(), amount=Decimal("1000.00"), product_category="Laptop & Accessory"))
    
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def test_priority_score_calculation():
    """Verify that weighted score calculations match the math model."""
    # High Churn (3.0) & Premium Segment (3.0) & Downward Trend (1.2)
    # Score = (0.6 * 3 + 0.4 * 3) * 1.2 = (1.8 + 1.2) * 1.2 = 3.0 * 1.2 = 3.60
    score1 = decision_engine.calculate_priority_score(churn_risk="High", segment="Premium", trend="Downward")
    assert pytest.approx(score1, 0.01) == 3.60
    assert decision_engine.get_priority_level(score1) == "High"

    # Low Churn (1.0) & Low-Value Segment (1.0) & Upward Trend (0.8)
    # Score = (0.6 * 1 + 0.4 * 1) * 0.8 = 1.0 * 0.8 = 0.8
    score2 = decision_engine.calculate_priority_score(churn_risk="Low", segment="Low-Value", trend="Upward")
    assert pytest.approx(score2, 0.01) == 0.8
    assert decision_engine.get_priority_level(score2) == "Low"

def test_recommendation_generation_rules():
    """Verify that the appropriate business rules match the risk, segment, and trend profiles."""
    db_session = TestingSessionLocal()
    customer = db_session.query(Customer).filter(Customer.id == "C-99999").first()
    
    # Case 1: High Churn + Premium Segment -> Critical VIP Alert (Retention)
    rec1 = decision_engine.generate_recommendation(
        customer=customer,
        churn_risk="High",
        segment="Premium",
        trend="Downward"
    )
    assert rec1.action_type == "retention action"
    assert rec1.priority == "High"
    assert "CRITICAL VIP ALERT" in rec1.recommendation_text
    
    # Case 2: Low Churn + Premium Segment -> Upsell Opportunity (Marketing)
    rec2 = decision_engine.generate_recommendation(
        customer=customer,
        churn_risk="Low",
        segment="Premium",
        trend="Stable"
    )
    assert rec2.action_type == "marketing suggestion"
    assert rec2.priority == "Medium"
    assert "PREMIUM UPSELL" in rec2.recommendation_text

    # Case 3: Low Churn + Regular Segment -> Standard Nurture (Next Best Action)
    rec3 = decision_engine.generate_recommendation(
        customer=customer,
        churn_risk="Low",
        segment="Regular",
        trend="Stable"
    )
    assert rec3.action_type == "next-best-action"
    assert rec3.priority == "Low"
    assert "STANDARD NURTURE" in rec3.recommendation_text
    
    db_session.close()
