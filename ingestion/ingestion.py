import os
import sys
import time
import requests
import logging
import pandas as pd
from prometheus_client import start_http_server, Counter, Gauge

# Add the model directory to the path so we can import the trigger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'model')))
from retrain_trigger import trigger_retraining
from drift_detector import detect_drift

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_URL = "http://149.40.228.124:6500/records"
POLL_INTERVAL = 30  # seconds
DATA_FILE = "ingested_data.csv"

# --- PROMETHEUS METRICS ---
records_processed_total = Counter('records_processed_total', 'Total number of records ingested')
feature_added = Counter('feature_added', 'Number of features added to the schema')
feature_removed = Counter('feature_removed', 'Number of features removed from the schema')
datalake_unavailable = Counter('datalake_unavailable', 'Times the /records endpoint returned 503')
distribution_drift_detected = Gauge('distribution_drift_detected', '1 if drift detected, 0 otherwise')

current_feature_count = None

def check_schema(batch):
    global current_feature_count
    if not batch:
        return
        
    new_feature_count = len(batch[0].get('features', []))
    
    if current_feature_count is None:
        current_feature_count = new_feature_count
        logging.info(f"Initial schema set: {current_feature_count} features detected.")
        return

    if new_feature_count > current_feature_count:
        diff = new_feature_count - current_feature_count
        logging.warning(f"SCHEMA ALERT: {diff} Feature(s) Added!")
        feature_added.inc(diff)  # Update Prometheus
        trigger_retraining("Schema change (Feature Added)")
        current_feature_count = new_feature_count
        
    elif new_feature_count < current_feature_count:
        diff = current_feature_count - new_feature_count
        logging.warning(f"SCHEMA ALERT: {diff} Feature(s) Removed!")
        feature_removed.inc(diff) # Update Prometheus
        trigger_retraining("Schema change (Feature Removed)")
        current_feature_count = new_feature_count

def save_data(batch):
    flat_data = []
    for record in batch:
        row = {f"feature_{i}": val for i, val in enumerate(record.get('features', []))}
        row['label'] = record.get('label')
        flat_data.append(row)
        
    df = pd.DataFrame(flat_data)
    write_header = not os.path.exists(DATA_FILE)
    df.to_csv(DATA_FILE, mode='a', index=False, header=write_header)
    
    logging.info(f"Saved {len(df)} records to {DATA_FILE}")
    records_processed_total.inc(len(df)) # Update Prometheus

def fetch_data():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data
            return None
        elif response.status_code == 503:
            logging.warning("Service Unavailable (503). Simulated downtime.")
            datalake_unavailable.inc() # Update Prometheus
            return None
        else:
            logging.error(f"Unexpected status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Connection error: {e}")
        return None

if __name__ == "__main__":
    logging.info("Starting Data Ingestion Service & Metrics Exporter on port 8001...")
    start_http_server(8001) 
    
    while True:
        batch = fetch_data()
        if batch:
            check_schema(batch)
            
            if os.path.exists(DATA_FILE):
                is_drifting = detect_drift(batch, DATA_FILE)
                if is_drifting:
                    distribution_drift_detected.set(1)
                    # trigger_retraining("Distribution Drift Detected")
                else:
                    distribution_drift_detected.set(0)
            
            save_data(batch)
            
        time.sleep(POLL_INTERVAL)