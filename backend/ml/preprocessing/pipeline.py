import os
import joblib
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

class DataPipeline:
    """
    Shared preprocessing pipeline for both training and inference.
    Isolates imputation, scaling, and encoding logic using real Kaggle dataset columns.
    """
    def __init__(self):
        # Define feature groups based on Kaggle dataset schema
        self.num_features = [
            "Tenure", "WarehouseToHome", "NumberOfDeviceRegistered",
            "SatisfactionScore", "NumberOfAddress", "Complain",
            "DaySinceLastOrder", "CashbackAmount"
        ]
        
        self.cat_features = ["MaritalStatus", "PreferedOrderCat"]
        self.pipeline = None
        self.feature_names_ = None

    def build_pipeline(self):
        """Constructs the scikit-learn Pipeline with ColumnTransformer."""
        # Numerical transformer: Impute missing values with median, then scale
        num_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])

        # Categorical transformer: Impute missing values with mode/constant, then One-Hot Encode
        cat_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="Others")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])

        # Combine into ColumnTransformer
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", num_transformer, self.num_features),
                ("cat", cat_transformer, self.cat_features)
            ],
            remainder="drop" # Drops ID, Name, Churn, or other extra fields
        )

        self.pipeline = Pipeline(steps=[("preprocessor", preprocessor)])

    def fit(self, df: pd.DataFrame):
        """Fits the pipeline on historical training data."""
        if self.pipeline is None:
            self.build_pipeline()
            
        self.pipeline.fit(df)
        
        # Capture generated feature names for traceability
        try:
            onehot_categories = self.pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["onehot"].get_feature_names_out(self.cat_features)
            self.feature_names_ = self.num_features + list(onehot_categories)
        except Exception:
            self.feature_names_ = None
            
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Applies fitted transformations to training or inference data."""
        if self.pipeline is None:
            raise ValueError("Pipeline has not been fitted yet. Please call fit() first.")
        return self.pipeline.transform(df)

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """Helper to fit and transform in one step."""
        self.fit(df)
        return self.transform(df)

    def save(self, path: str):
        """Serializes and saves the pipeline object to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)
        print(f"Data pipeline saved successfully to {path}")

    @staticmethod
    def load(path: str) -> "DataPipeline":
        """Loads and returns a serialized DataPipeline object."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Pipeline file not found at {path}")
        pipeline_obj = joblib.load(path)
        print(f"Data pipeline loaded successfully from {path}")
        return pipeline_obj
