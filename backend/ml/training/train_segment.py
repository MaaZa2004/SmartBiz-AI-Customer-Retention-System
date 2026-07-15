import os
import sys
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib

# Inject backend path into sys.path to enable imports
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

"""
--- DOCUMENTATION: SELECTING OPTIMAL K ---
We chose K=3 clusters for Customer Segmentation to divide customers into three distinct tier categories:
1. Premium (High value/cashback, high engagement)
2. Regular (Moderate value/cashback)
3. Low-Value (Low value/cashback)

We evaluate silhouette scores and sum of squared distances on the real Kaggle features (Tenure, CashbackAmount, SatisfactionScore, NumberOfAddress).
"""

def train_segmentation_model():
    print("--- Starting Customer Segmentation Model Training ---")
    
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

    # 2. Extract Clustering Features
    features = ["Tenure", "CashbackAmount", "SatisfactionScore", "NumberOfAddress"]
    X = df[features].copy()
    
    # Handle nulls by filling with median
    X = X.fillna(X.median())

    # 3. Scale Features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Save Scaler for Inference
    scaler_save_path = os.path.join(saved_models_dir, "segment_scaler.pkl")
    joblib.dump(scaler, scaler_save_path)
    print(f"Segmentation scaler saved successfully to {scaler_save_path}")

    # 4. Train K-Means (K=3)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    labels = kmeans.labels_
    
    # 5. Map Clusters to Semantic Tiers consistently by Mean CashbackAmount
    df_temp = X.copy()
    df_temp["cluster"] = labels
    cluster_cashback = df_temp.groupby("cluster")["CashbackAmount"].mean().sort_values()
    
    cluster_order = list(cluster_cashback.index)
    mapping = {
        cluster_order[0]: "Low-Value",
        cluster_order[1]: "Regular",
        cluster_order[2]: "Premium"
    }
    
    print("\nCluster Mapping Analysis:")
    for cluster, label in mapping.items():
        mean_cash = cluster_cashback.loc[cluster]
        count = len(df_temp[df_temp["cluster"] == cluster])
        print(f"Cluster {cluster} -> Label: {label:10} (Count: {count:4}, Mean Cashback: ${mean_cash:.2f})")
    
    # 6. Save Model and Mapping
    model_data = {
        "kmeans": kmeans,
        "mapping": mapping,
        "feature_names": features
    }
    
    model_save_path = os.path.join(saved_models_dir, "segment_model.pkl")
    joblib.dump(model_data, model_save_path)
    print(f"Segmentation model data saved successfully to {model_save_path}")
    print("--- Training Completed ---")

if __name__ == "__main__":
    train_segmentation_model()
