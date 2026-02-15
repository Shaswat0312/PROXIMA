import joblib
import numpy as np
import os

# ===============================
# MODEL CACHE (Persists in RAM)
# ===============================
# This dictionary stores models after they are loaded the first time.
_model_cache = {}

def load_region_model(region):
    """Loads model from disk only once, then serves from memory."""
    if region not in _model_cache:
        model_path = f"models/{region}_model.pkl"
        
        if not os.path.exists(model_path):
            # This helps you debug if a specific region file is missing
            raise FileNotFoundError(f"Model file for {region} not found at {model_path}")
        
        # Load into memory
        _model_cache[region] = joblib.load(model_path)
        print(f"--- Loaded {region} model into memory ---")
        
    return _model_cache[region]


# ===============================
# FORECAST FUNCTION (XGBOOST)
# ===============================

def forecast_next_demand(region, lag_24, lag_168, hour, month):
    # This now pulls from the cache instead of the slow hard drive
    model = load_region_model(region)

    # Create seasonal features (same as training)
    sin_month = np.sin(2 * np.pi * month / 12)
    cos_month = np.cos(2 * np.pi * month / 12)

    # Arrange features in SAME ORDER as training
    features = np.array([[
        lag_24,
        lag_168,
        hour,
        sin_month,
        cos_month
    ]])

    prediction = model.predict(features)[0]

    return float(prediction)