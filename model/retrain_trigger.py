import subprocess
import logging
import sys
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def trigger_retraining(reason):
    logging.info(f"RETRAINING TRIGGERED. Reason: {reason}")
    
    try:
        # Determine the path to train.py relative to this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        train_script_path = os.path.join(current_dir, "train.py")
        
        # Execute the training script as a separate process
        result = subprocess.run(
            [sys.executable, train_script_path], 
            capture_output=True, 
            text=True
        )
        
        if "Success! Model saved" in result.stdout:
            logging.info("Auto-retraining completed successfully!")
            # Note: We will add the Prometheus retrain_count_total increment 
            # and the Slack notification here in Parts 4 & 6.
            return True
        else:
            logging.warning("Auto-retraining ran, but target accuracy was not met or an error occurred.")
            logging.debug(f"Training output: {result.stdout}")
            return False
            
    except Exception as e:
        logging.error(f"Failed to execute retraining pipeline: {e}")
        return False

if __name__ == "__main__":
    # For manual testing purposes
    trigger_retraining("Manual test execution")