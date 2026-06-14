import threading
import requests
import time

TARGET_URL = "http://35.178.253.225:8000/predict"
payload = {"features": [0.5, 1.2]}

# We will run this continuously for 45 seconds to force a massive spike
RUN_TIME_SECONDS = 45  
CONCURRENT_USERS = 20

def send_request():
    # Keep firing requests until the timer runs out
    while time.time() < end_time:
        try:
            requests.post(TARGET_URL, json=payload, timeout=2)
        except requests.exceptions.RequestException:
            pass 

def run_stress_test():
    print(f"🚀 Blasting the ML Model with traffic for {RUN_TIME_SECONDS} seconds...")
    print("Wait for the timer to finish!")
    
    global end_time
    end_time = time.time() + RUN_TIME_SECONDS
    
    threads = []
    for _ in range(CONCURRENT_USERS):
        t = threading.Thread(target=send_request)
        threads.append(t)
        t.start()
            
    for t in threads:
        t.join()
        
    print("✅ Traffic wave complete! Go to Grafana and click REFRESH.")

if __name__ == "__main__":
    run_stress_test()