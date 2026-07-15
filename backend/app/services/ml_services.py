import os
import joblib
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.models.models import Customer, Sale
from app.schemas.schemas import ChurnPredictResponse, SegmentPredictResponse, ForecastPredictResponse

# Resolve directories relative to this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "ml", "saved_models"))

class MLService:
    """
    Service wrapper for loading serialized ML models and running inference.
    Aligned with the real Kaggle customer churn dataset features.
    """
    def __init__(self):
        self.pipeline = None
        self.churn_model = None
        self.segment_model = None
        self.forecast_model = None
        
        self.models_loaded = False

    def load_models(self):
        """Loads serialized models into memory if not already loaded."""
        if self.models_loaded:
            return

        pipeline_path = os.path.join(MODELS_DIR, "pipeline.pkl")
        churn_path = os.path.join(MODELS_DIR, "churn_model.pkl")
        segment_path = os.path.join(MODELS_DIR, "segment_model.pkl")
        forecast_path = os.path.join(MODELS_DIR, "forecast_model.pkl")

        try:
            if os.path.exists(pipeline_path):
                # Load preprocessing pipeline
                self.pipeline = joblib.load(pipeline_path)
            
            if os.path.exists(churn_path):
                self.churn_model = joblib.load(churn_path)
                
            if os.path.exists(segment_path):
                self.segment_model = joblib.load(segment_path)
                
            if os.path.exists(forecast_path):
                self.forecast_model = joblib.load(forecast_path)
                
            self.models_loaded = True
            print("ML models loaded successfully.")
        except Exception as e:
            print(f"Warning: Failed to load serialized models: {e}. Models must be trained first.")

    def predict_customer_churn(self, customer: Customer) -> ChurnPredictResponse:
        """Runs Churn Prediction on a single customer record."""
        self.load_models()
        if not self.churn_model or not self.pipeline:
            raise ValueError("Churn model or pipeline not loaded. Please run model training first.")

        # Convert customer model instance to DataFrame using exact Kaggle schema keys
        cust_dict = {
            "Tenure": [customer.tenure],
            "WarehouseToHome": [customer.warehouse_to_home],
            "NumberOfDeviceRegistered": [customer.num_devices_registered],
            "PreferedOrderCat": [customer.product_category],
            "SatisfactionScore": [customer.satisfaction_score],
            "MaritalStatus": [customer.marital_status],
            "NumberOfAddress": [customer.num_addresses],
            "Complain": [customer.complain],
            "DaySinceLastOrder": [customer.days_since_last_order],
            "CashbackAmount": [float(customer.cashback_amount) if customer.cashback_amount is not None else 0.0]
        }
        df = pd.DataFrame(cust_dict)
        
        # Preprocess using pipeline
        X_processed = self.pipeline.transform(df)
        
        # Run inference
        prob = float(self.churn_model.predict_proba(X_processed)[0, 1])
        
        # Assign risk level based on thresholds
        if prob < 0.35:
            risk_level = "Low"
        elif prob < 0.65:
            risk_level = "Medium"
        else:
            risk_level = "High"
            
        return ChurnPredictResponse(
            customer_id=customer.id,
            churn_probability=prob,
            risk_level=risk_level
        )

    def predict_customer_segment(self, customer: Customer) -> SegmentPredictResponse:
        """Runs Segmentation on a single customer record."""
        self.load_models()
        if not self.segment_model:
            raise ValueError("Segmentation model not loaded. Please run model training first.")

        scaler_path = os.path.join(MODELS_DIR, "segment_scaler.pkl")
        if not os.path.exists(scaler_path):
            raise ValueError("Segmentation scaler not found.")
            
        scaler = joblib.load(scaler_path)
        
        # Extract features: Tenure, CashbackAmount, SatisfactionScore, NumberOfAddress
        tenure = customer.tenure if customer.tenure is not None else 0
        cashback = float(customer.cashback_amount) if customer.cashback_amount is not None else 0.0
        satisfaction = customer.satisfaction_score if customer.satisfaction_score is not None else 3
        address = customer.num_addresses if customer.num_addresses is not None else 1
        
        features_arr = np.array([[tenure, cashback, satisfaction, address]])
        
        # Scale
        features_scaled = scaler.transform(features_arr)
        
        # Predict K-Means cluster
        cluster = int(self.segment_model["kmeans"].predict(features_scaled)[0])
        
        # Map to label
        segment_label = self.segment_model["mapping"].get(cluster, "Regular")
        
        details = {
            "cluster_id": cluster,
            "tenure_months": tenure,
            "cashback_amount": cashback,
            "satisfaction_score": satisfaction,
            "address_count": address
        }
        
        return SegmentPredictResponse(
            customer_id=customer.id,
            segment=segment_label,
            details=details
        )

    def predict_sales_forecast(self, category: str, db: Session, forecast_days: int = 30) -> ForecastPredictResponse:
        """Runs Sales Forecasting for a specific product category using Random Forest."""
        self.load_models()
        if not self.forecast_model:
            raise ValueError("Forecasting model not loaded. Please run model training first.")

        # Get all customers belonging to this category
        customers = db.query(Customer).filter(Customer.product_category == category).all()
        if not customers:
            # Fallback if no customers, return a basic prediction based on average stats
            dummy_cust = pd.DataFrame({
                "PreferedOrderCat": [category],
                "Tenure": [12],
                "SatisfactionScore": [3],
                "WarehouseToHome": [15],
                "CashbackAmount": [150.0]
            })
            pred_val = float(self.forecast_model.predict(dummy_cust)[0]) * 10 # scale for category
            return ForecastPredictResponse(
                product_category=category,
                expected_sales_value=pred_val,
                trend_direction="Stable"
            )

        # Create feature dataframe for all customers in this category
        cust_list = []
        actual_total_monthly = 0.0
        for cust in customers:
            actual_total_monthly += float(cust.total_spending / max(1, cust.tenure or 12)) # approx monthly spend
            cust_list.append({
                "PreferedOrderCat": category,
                "Tenure": cust.tenure or 12,
                "SatisfactionScore": cust.satisfaction_score or 3,
                "WarehouseToHome": cust.warehouse_to_home or 15,
                "CashbackAmount": float(cust.cashback_amount) if cust.cashback_amount is not None else 0.0
            })
            
        df = pd.DataFrame(cust_list)
        
        # Predict monthly sales for each customer using Random Forest Regressor
        predictions = self.forecast_model.predict(df)
        expected_sales_value = float(np.sum(predictions))
        
        # Calculate trend direction by comparing expected sales with approximate monthly actuals
        diff = expected_sales_value - actual_total_monthly
        pct_change = (diff / actual_total_monthly) if actual_total_monthly > 0 else 0
        
        if pct_change > 0.05:
            trend_direction = "Upward"
        elif pct_change < -0.05:
            trend_direction = "Downward"
        else:
            trend_direction = "Stable"
            
        return ForecastPredictResponse(
            product_category=category,
            expected_sales_value=expected_sales_value,
            trend_direction=trend_direction
        )

# Instantiate singleton service instance
ml_service = MLService()
