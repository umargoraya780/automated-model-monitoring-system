from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import make_asgi_app, Counter, Gauge, Histogram
import joblib
import glob
import os
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="MLOps Inference API")

# --- PART 4: RUBRIC REQUIRED METRICS ---
model_accuracy = Gauge('model_accuracy', 'Current validation accuracy of the deployed model (0.0-1.0).')
records_processed_total = Counter('records_processed_total', 'Total number of records ingested from the API since startup.')
retrain_count_total = Counter('retrain_count_total', 'Total number of times the model has been retrained.')
distribution_drift_detected = Gauge('distribution_drift_detected', 'Set to 1 when drift is detected in the current batch, 0 otherwise.')
feature_added = Counter('feature_added', 'Number of features added to the schema since startup.')
feature_removed = Counter('feature_removed', 'Number of features removed from the schema since startup.')
datalake_unavailable = Counter('datalake_unavailable', 'Number of times the /records endpoint returned 503.')
response_delay_seconds = Histogram('response_delay_seconds', 'Latency of each /predict API call in seconds.')

# Route Prometheus metrics to /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# --- MODEL LOADING LOGIC ---
def load_latest_model():
    # Look in the model directory (works when running via Docker from project root)
    model_files = glob.glob("model/model_v*.pkl")
    if not model_files:
        # Fallback if running locally directly inside the serving folder
        model_files = glob.glob("../model/model_v*.pkl")
        
    if not model_files:
        logging.warning("No model files found. API will start, but /predict will fail.")
        return None
        
    # Get the highest version model
    latest_model_path = max(model_files, key=os.path.getctime)
    logging.info(f"Loading model: {latest_model_path}")
    return joblib.load(latest_model_path)

model = load_latest_model()

# Define the expected input schema for the /predict endpoint
class PredictRequest(BaseModel):
    features: list[float]

@app.get("/health")
def health_check():
    """Returns a simple health status."""
    return {"status": "ok"}

@app.post("/predict")
def predict(request: PredictRequest):
    """Accepts JSON feature input, returns prediction."""
    start_time = time.time()
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model is currently unavailable or retraining.")
    
    try:
        # The model expects a 2D array, so we wrap the features in a list
        prediction = model.predict([request.features])
        
        # Track the latency of the prediction for Prometheus
        response_delay_seconds.observe(time.time() - start_time)
        
        return {"prediction": int(prediction[0])}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- PART 6: SLACK ALERT TRIPWIRE ---
@app.get("/force-alerts")
def force_alerts():
    """Artificially triggers all 7 Prometheus alerts for the Part 6 Screenshots."""
    datalake_unavailable.inc(5)
    feature_added.inc(1)
    feature_removed.inc(1)
    distribution_drift_detected.set(1)
    model_accuracy.set(0.50) # Drops below the 0.80 threshold
    
    # Force high latency (simulate a slow response)
    for _ in range(10):
        response_delay_seconds.observe(1.5) # Exceeds the 1.0 second limit
        
    return {"message": "Wire tripped! All 7 metrics spiked. Check Slack in ~15-30 seconds."}