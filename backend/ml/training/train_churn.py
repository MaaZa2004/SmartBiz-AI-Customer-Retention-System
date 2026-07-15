import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score
import joblib

# Inject backend path into sys.path to enable imports
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from ml.preprocessing.pipeline import DataPipeline

def train_churn_model():
    print("--- Starting Churn Prediction Model Training ---")
    
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

    # 2. Setup preprocessing pipeline
    pipeline = DataPipeline()
    
    # Separate features and target
    X = df.drop(columns=["Churn"])
    y = df["Churn"]
    
    # Fit and transform features
    X_processed = pipeline.fit_transform(X)
    
    # Save preprocessing pipeline for inference
    pipeline_save_path = os.path.join(saved_models_dir, "pipeline.pkl")
    pipeline.save(pipeline_save_path)
    
    # 3. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_processed, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 4. Train Logistic Regression Model
    # Using class_weight='balanced' to handle any slight label imbalances
    model = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    
    # 5. Evaluate Model
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    
    print("\n--- Model Evaluation Results ---")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"ROC-AUC Score: {roc_auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # 6. Save Model
    model_save_path = os.path.join(saved_models_dir, "churn_model.pkl")
    joblib.dump(model, model_save_path)
    print(f"Churn prediction model saved successfully to {model_save_path}")
    print("--- Training Completed ---")

if __name__ == "__main__":
    train_churn_model()
