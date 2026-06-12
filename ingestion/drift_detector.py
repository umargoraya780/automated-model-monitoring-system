import pandas as pd
import numpy as np
import logging

# We will flag drift if the new mean is more than 1.5 standard deviations away from the baseline
DRIFT_THRESHOLD = 1.5 

def detect_drift(new_batch, baseline_csv_path="ingested_data.csv"):
    try:
        # 1. Load historical baseline data
        df_baseline = pd.read_csv(baseline_csv_path)
        
        # We only care about feature columns, not the label
        feature_cols = [col for col in df_baseline.columns if col.startswith('feature_')]
        
        # If we don't have enough data to form a reliable baseline yet, skip detection
        if len(df_baseline) < 50: 
            return False
            
        baseline_stats = df_baseline[feature_cols].describe().T
        
        # 2. Process the incoming new batch
        flat_data = []
        for record in new_batch:
            row = {f"feature_{i}": val for i, val in enumerate(record.get('features', []))}
            flat_data.append(row)
        df_new = pd.DataFrame(flat_data)
        
        drift_detected = False
        
        # 3. Compare statistics
        for col in feature_cols:
            if col in df_new.columns:
                new_mean = df_new[col].mean()
                base_mean = baseline_stats.loc[col, 'mean']
                base_std = baseline_stats.loc[col, 'std']
                
                # Prevent division by zero if there is no variance yet
                if base_std == 0:
                    continue
                    
                # Calculate how far the new mean is from the baseline mean
                z_score = abs(new_mean - base_mean) / base_std
                
                if z_score > DRIFT_THRESHOLD:
                    logging.warning(f"DRIFT ALERT: {col} mean shifted significantly! (Z-score: {z_score:.2f})")
                    drift_detected = True
                    
        return drift_detected
        
    except Exception as e:
        logging.error(f"Error in drift detection: {e}")
        return False