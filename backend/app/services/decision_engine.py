from sqlalchemy.orm import Session
from app.models.models import Customer, Prediction, Recommendation
from app.schemas.schemas import ChurnPredictResponse, SegmentPredictResponse, ForecastPredictResponse
from app.services.ml_services import ml_service

class DecisionEngine:
    """
    Core Decision Intelligence Engine.
    Combines outputs of Churn Prediction, Customer Segmentation, and Sales Forecasting 
    to output high-priority 'next-best-action', 'retention', and 'marketing' recommendations.
    """
    
    @staticmethod
    def calculate_priority_score(churn_risk: str, segment: str, trend: str) -> float:
        """
        Computes a numerical priority score using a weighted scoring model:
        Score = (ChurnWeight * ChurnScore + SegmentWeight * SegmentScore) * TrendMultiplier
        """
        # 1. Churn Risk Score (60% weight)
        churn_scores = {"High": 3.0, "Medium": 2.0, "Low": 1.0}
        c_score = churn_scores.get(churn_risk, 1.0)
        
        # 2. Segment Score (40% weight)
        segment_scores = {"Premium": 3.0, "Regular": 2.0, "Low-Value": 1.0}
        s_score = segment_scores.get(segment, 1.0)
        
        # 3. Forecast Trend Multiplier (downward trend increases urgency)
        trend_multipliers = {"Downward": 1.2, "Stable": 1.0, "Upward": 0.8}
        t_mult = trend_multipliers.get(trend, 1.0)
        
        # Weighted computation
        weighted_score = (0.6 * c_score) + (0.4 * s_score)
        priority_score = weighted_score * t_mult
        return priority_score

    @staticmethod
    def get_priority_level(score: float) -> str:
        """Categorizes numerical priority score into High, Medium, Low."""
        if score >= 2.2:
            return "High"
        elif score >= 1.5:
            return "Medium"
        else:
            return "Low"

    def generate_recommendation(
        self, 
        customer: Customer, 
        churn_risk: str, 
        segment: str, 
        trend: str
    ) -> Recommendation:
        """
        Executes business decision rules to output the optimal retention action, 
        marketing campaign, or next-best-action.
        """
        score = self.calculate_priority_score(churn_risk, segment, trend)
        priority = self.get_priority_level(score)
        
        category = customer.product_category or "general merchandise"
        
        # --- RULE DIRECTORY ---
        # Rule 1: High Churn + Premium Segment
        if churn_risk == "High" and segment == "Premium":
            rec_text = (
                f"CRITICAL VIP ALERT: Customer is a Premium buyer at high risk of churn, "
                f"compounded by a {trend.lower()} trend in {category}. Immediately assign a "
                f"dedicated Account Executive, issue an exclusive 20% cashback loyalty offer, "
                f"and schedule a direct call to resolve complains."
            )
            action_type = "retention action"
            
        # Rule 2: High Churn + Regular Segment
        elif churn_risk == "High" and segment == "Regular":
            rec_text = (
                f"AT-RISK REGULAR CUSTOMER: Customer is churn-prone. Trigger an automated "
                f"personal outreach email containing a 15% discount voucher valid for 7 days "
                f"on {category}, and prioritize any open support tickets."
            )
            action_type = "retention action"
            
        # Rule 3: Medium Churn + Premium Segment
        elif churn_risk == "Medium" and segment == "Premium":
            rec_text = (
                f"VIP ENGAGEMENT NEEDED: Premium customer exhibiting early warning signs of churn. "
                f"Invite them to the VIP Early-Access program and suggest a complimentary "
                f"loyalty gift card to increase positive sentiment."
            )
            action_type = "next-best-action"
            
        # Rule 4: Low Churn + Premium Segment
        elif churn_risk == "Low" and segment == "Premium":
            rec_text = (
                f"PREMIUM UPSELL OPPORTUNITY: High-value, loyal customer. Invite to exclusive "
                f"beta testing for high-margin {category} releases, and offer personal shopping "
                f"consultation incentives."
            )
            action_type = "marketing suggestion"
            
        # Rule 5: High Churn + Low-Value Segment
        elif churn_risk == "High" and segment == "Low-Value":
            rec_text = (
                f"RE-ENGAGEMENT RETENTION: Low-cost retention campaign. Send automated "
                f"re-engagement email highlighting trending clearance deals or affordable alternatives "
                f"in {category}."
            )
            action_type = "retention action"
            
        # Rule 6: Low Churn + Regular Segment
        elif churn_risk == "Low" and segment == "Regular":
            rec_text = (
                f"STANDARD NURTURE: Normal loyal customer. Maintain standard quarterly touchpoints, "
                f"suggest accessories in {category}, and provide a seasonal thank-you reward point booster."
            )
            action_type = "next-best-action"
            
        # Default Fallback: Low Churn + Low-Value
        else:
            rec_text = (
                f"LOW-COST ENGAGEMENT: Loyal low-tier customer. Include in weekly automated "
                f"newsletter campaigns promoting standard discounts and bulk order incentives."
            )
            action_type = "marketing suggestion"

        # Construct and return Recommendation model
        return Recommendation(
            customer_id=customer.id,
            recommendation_text=rec_text,
            action_type=action_type,
            priority=priority
        )

    def run_for_customer(self, db: Session, customer_id: str) -> Recommendation:
        """
        Runs churn, segment, and forecast predictions for a customer, 
        feeds outputs to decision logic, saves, and returns the recommendation.
        """
        # 1. Fetch customer
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")

        # 2. Run model inferences
        # Churn Prediction
        churn_res = ml_service.predict_customer_churn(customer)
        # Segmentation
        segment_res = ml_service.predict_customer_segment(customer)
        # Category Sales Forecast
        category = customer.product_category or "Others"
        forecast_res = ml_service.predict_sales_forecast(category, db)

        # 3. Save prediction logs to DB
        db.add(Prediction(
            customer_id=customer_id, 
            model_type="churn", 
            result_value=f"{churn_res.churn_probability:.4f} ({churn_res.risk_level})",
            confidence_score=churn_res.churn_probability
        ))
        db.add(Prediction(
            customer_id=customer_id,
            model_type="segment",
            result_value=segment_res.segment,
            confidence_score=1.0
        ))
        db.add(Prediction(
            customer_id=customer_id,
            model_type="forecast",
            result_value=f"{forecast_res.expected_sales_value:.2f}",
            confidence_score=None
        ))
        
        # Update customer table properties if they differ
        customer.churn = 1 if churn_res.risk_level == "High" else 0
        
        # 4. Run Decision Logic
        rec = self.generate_recommendation(
            customer=customer,
            churn_risk=churn_res.risk_level,
            segment=segment_res.segment,
            trend=forecast_res.trend_direction
        )
        
        # Save recommendation to DB
        db.add(rec)
        db.commit()
        db.refresh(rec)
        
        return rec

# Instantiate singleton decision engine
decision_engine = DecisionEngine()
