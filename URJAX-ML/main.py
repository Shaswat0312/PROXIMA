import os
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from ml import forecast_next_demand

# ===============================
# FASTAPI INIT
# ===============================
app = FastAPI(title="IdleGrid AI - Intelligent Grid Analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# GEMINI CONFIG
# ===============================
GEMINI_KEY = os.getenv("GEMINI_KEY")


client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

MODEL_PRIORITY = [
    "gemini-1.5-flash-002",
    "gemini-1.5-flash"
]

DEFAULT_POLICY = (
    "Grid health is currently at Moderate Risk. "
    "Utilization metrics suggest structural imbalances between supply and demand. "
    "Immediate action: Deploy localized demand-response protocols. "
    "Long-term: Invest in grid-scale storage to mitigate residual variance."
)

# ===============================
# REGIONS
# ===============================
REGIONS = ["Northern", "Western", "Eastern", "Southern", "North-Eastern"]

# ===============================
# MODEL CACHE
# ===============================
score_scalers = {}
isolation_models = {}

@app.on_event("startup")
async def startup_event():
    for region in REGIONS:
        scaler_path = f"models/{region}_scaler.pkl"
        iso_path = f"models/{region}_isolation.pkl"

        if os.path.exists(scaler_path):
            score_scalers[region] = joblib.load(scaler_path)

        if os.path.exists(iso_path):
            isolation_models[region] = joblib.load(iso_path)

    print("🚀 Models loaded successfully.")


# ===============================
# SCHEMAS
# ===============================
class AnalysisInput(BaseModel):
    region: str
    lag_24: float
    lag_168: float
    hour: int
    month: int
    actual_demand: float
    supply: float


class RegionLoad(BaseModel):
    region: str
    predicted_demand: float
    supply: float


class DistributionInput(BaseModel):
    regions: list[RegionLoad]


# ===============================
# ROUTES
# ===============================
@app.get("/")
def home():
    return {"message": "IdleGrid AI Backend Running 🚀"}


@app.post("/analyze")
def analyze(data: AnalysisInput):

    if data.region not in REGIONS:
        raise HTTPException(status_code=400, detail="Invalid region")

    # 1️⃣ Forecast
    try:
        predicted_demand = forecast_next_demand(
            region=data.region,
            lag_24=data.lag_24,
            lag_168=data.lag_168,
            hour=data.hour,
            month=data.month
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML Forecast Error: {str(e)}")

    # 2️⃣ Core Metrics
    gap = data.supply - predicted_demand
    utilization = predicted_demand / (data.supply + 1e-6)
    residual = data.actual_demand - predicted_demand

    anomaly_flag = 0
    inefficiency_score = 0.0

    # 3️⃣ Isolation Forest
    if data.region in isolation_models:
        iso_model = isolation_models[data.region]
        iso_input = [[utilization, residual, gap]]
        anomaly_pred = iso_model.predict(iso_input)[0]
        anomaly_flag = 1 if anomaly_pred == -1 else 0

    # 4️⃣ Inefficiency Score (CLAMPED SAFE)
    if data.region in score_scalers:
        scaler = score_scalers[data.region]
        scaled = scaler.transform([[utilization, residual, gap]])

        scaled_util = float(np.clip(scaled[0][0], 0, 1))
        scaled_res  = float(np.clip(scaled[0][1], 0, 1))
        scaled_gap  = float(np.clip(scaled[0][2], 0, 1))

        raw_score = (
            (1 - scaled_util) * 0.40 +
            scaled_res * 0.30 +
            scaled_gap * 0.20 +
            anomaly_flag * 0.10
        )

        inefficiency_score = float(np.clip(raw_score, 0, 1))

    # 5️⃣ Gemini Policy
    policy = DEFAULT_POLICY

    if client:
        prompt = f"""
You are a national energy grid optimization expert.

Region: {data.region}
Predicted Demand: {predicted_demand:.2f}
Actual Demand: {data.actual_demand:.2f}
Supply: {data.supply:.2f}
Utilization: {utilization:.3f}
Residual: {residual:.2f}
Inefficiency Score: {inefficiency_score:.4f}
Anomaly Detected: {"Yes" if anomaly_flag else "No"}

Respond in 4 professional sentences:
1. Classify grid health
2. Explain structural inefficiency
3. Recommend immediate intervention
4. Suggest long-term infrastructure strategy
"""

        for model_id in MODEL_PRIORITY:
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt
                )
                if response and response.text:
                    policy = response.text
                    break
            except Exception as e:
                print(f"Gemini failed for {model_id}: {e}")

    return {
        "region": data.region,
        "predicted_demand": float(predicted_demand),
        "actual_demand": data.actual_demand,
        "supply": data.supply,
        "gap": float(gap),
        "utilization_percent": float(utilization * 100),
        "residual": float(residual),
        "anomaly_flag": anomaly_flag,
        "inefficiency_score": inefficiency_score,
        "policy_recommendation": policy
    }


# ===============================
# DISTRIBUTION LOGIC
# ===============================
def compute_distribution(regions):

    surplus_regions = []
    deficit_regions = []
    total_surplus = 0
    total_deficit = 0

    for r in regions:
        gap = r.supply - r.predicted_demand

        if gap > 0:
            surplus_regions.append({"region": r.region, "gap": gap})
            total_surplus += gap
        elif gap < 0:
            deficit_regions.append({"region": r.region, "gap": abs(gap)})
            total_deficit += abs(gap)

    transfer_plan = []

    for deficit in deficit_regions:
        needed = deficit["gap"]

        for surplus in surplus_regions:
            if total_surplus == 0:
                continue

            share_ratio = surplus["gap"] / total_surplus
            transfer_amount = share_ratio * needed

            transfer_plan.append({
                "from": surplus["region"],
                "to": deficit["region"],
                "power_transfer": round(transfer_amount, 2)
            })

    return {
        "total_surplus": total_surplus,
        "total_deficit": total_deficit,
        "transfer_plan": transfer_plan
    }


@app.post("/optimize-distribution")
def optimize_distribution(data: DistributionInput):

    if len(data.regions) == 0:
        raise HTTPException(status_code=400, detail="No regions provided")

    return compute_distribution(data.regions)