import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import logging
import os
import glob

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Assuming you run this from the 'model' directory
DATA_PATH = "../ingestion/ingested_data.csv"

def get_next_version():
    """Finds the highest version model and increments by 1."""
    existing_models = glob.glob("model_v*.pkl")
    if not existing_models:
        return 1
    versions = [int(f.split('_v')[-1].split('.pkl')[0]) for f in existing_models]
    return max(versions) + 1

def train_model():
    if not os.path.exists(DATA_PATH):
        logging.error(f"Data file {DATA_PATH} not found. Let the ingestion script run longer.")
        return False

    # 1. Load the data
    df = pd.read_csv(DATA_PATH)
    
    if len(df) < 50:
        logging.warning(f"Only {len(df)} records found. Waiting for more data to train a reliable model.")
        return False

    # 2. Prepare Features (X) and Labels (y)
    feature_cols = [col for col in df.columns if col.startswith('feature_')]
    X = df[feature_cols]
    y = df['label']

    # Split into 80% training and 20% validation
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Train the Classifier
    logging.info("Training Random Forest Classifier...")
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X_train, y_train)

    # 4. Evaluate Accuracy
    preds = clf.predict(X_val)
    accuracy = accuracy_score(y_val, preds)
    
    logging.info(f"Validation Accuracy: {accuracy:.4f}")

    # 5. Check Threshold and Serialize Model
    if accuracy >= 0.80:
        version = get_next_version()
        model_filename = f"model_v{version}.pkl"
        joblib.dump(clf, model_filename)
        logging.info(f"Success! Model saved as {model_filename}")
        return True
    else:
        logging.warning("Failed to reach target accuracy of 0.80. Model not saved.")
        return False

if __name__ == "__main__":
    train_model()