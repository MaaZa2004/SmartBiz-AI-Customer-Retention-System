import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Inject backend path into sys.path to enable imports
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

def train_forecasting_model():
    print("--- Starting Sales Forecasting Model Training ---")
    
    # Define file paths
    data_dir = os.path.join(base_dir, "ml", "data")
    saved_models_dir = os.path.join(base_dir, "ml", "saved_models")
    os.makedirs(saved_models_dir, exist_ok=True)
    
    csv_path = os.path.join(data_dir, "ecommerce_customer_churn.csv")
    
    # 1. Load Dataset
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Kaggle customer churn dataset not found at {csv_path}. Please import it first.")
        
    df = pd.read_csv(csv_path)
    print(f"Loaded Kaggle dataset with {len(df)} records.")

    # 2. Synthesize target MonthlySales based on actual client attributes
    # We create a realistic target representing customer monthly spending volume.
    # Total monthly sales correlates positively with CashbackAmount and Tenure.
    np.random.seed(42)
    tenure_filled = df["Tenure"].fillna(df["Tenure"].median())
    cashback_filled = df["CashbackAmount"].fillna(df["CashbackAmount"].median())
    
    # Formula: cashback * 9.5 + tenure * 4.5 + random variance
    noise = np.random.normal(0, 15, len(df))
    df["MonthlySales"] = np.round((cashback_filled * 9.5) + (tenure_filled * 4.5) + noise, 2)
    # Clamp negative sales to a baseline minimum purchase
    df["MonthlySales"] = df["MonthlySales"].clip(lower=15.00)

    # 3. Prepare Features & Target
    features = ["PreferedOrderCat", "Tenure", "SatisfactionScore", "WarehouseToHome", "CashbackAmount"]
    X = df[features]
    y = df["MonthlySales"]

    # 4. Build preprocessing + model pipeline
    cat_cols = ["PreferedOrderCat"]
    num_cols = ["Tenure", "SatisfactionScore", "WarehouseToHome", "CashbackAmount"]

    num_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median"))
    ])

    cat_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="Others")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, num_cols),
            ("cat", cat_transformer, cat_cols)
        ]
    )

    # Random Forest Regressor
    model_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
    ])

    # 5. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 6. Fit Model
    model_pipeline.fit(X_train, y_train)

    # 7. Evaluate
    y_pred = model_pipeline.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("\n--- Model Evaluation Results ---")
    print(f"Root Mean Squared Error (RMSE): ${rmse:.4f}")
    print(f"R-squared Score: {r2:.4f}")

    # 8. Save Model
    model_save_path = os.path.join(saved_models_dir, "forecast_model.pkl")
    joblib.dump(model_pipeline, model_save_path)
    print(f"Sales forecasting model saved successfully to {model_save_path}")
    print("--- Training Completed ---")

if __name__ == "__main__":
    train_forecasting_model()
