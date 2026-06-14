# 🛡️ Automated MLOps Safety Monitoring Platform

![Build Status](https://img.shields.io/badge/build-passing-brightgreen) ![Docker](https://img.shields.io/badge/Docker-Enabled-blue) ![AWS](https://img.shields.io/badge/AWS-EC2-orange) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-teal)

This repository contains the core microservices, machine learning inference API, and automated observability pipeline developed for my Final Year Project at FAST NUCES. It demonstrates a production-grade MLOps architecture designed to monitor system health, track data drift, and route automated alerts in real-time.

**Author:** Umar Nadeem Goraya

---

## 🏗️ Architecture Overview
The system relies on a containerized microservices architecture to serve a Random Forest Machine Learning model while simultaneously tracking its performance and infrastructural stability under heavy load. 

The architecture is divided into three main layers:
1. **Serving Layer:** A FastAPI application exposing the ML model and health endpoints.
2. **Observability Layer:** Prometheus for time-series metrics scraping and Grafana for real-time dashboard visualization.
3. **Incident Management Layer:** Alertmanager integrated with Slack Webhooks to notify operations teams of system degradation or data anomalies.

## 💻 Tech Stack
* **Backend & API:** Python, FastAPI, Uvicorn
* **Machine Learning:** Scikit-Learn (RandomForestClassifier)
* **Observability:** Prometheus, Grafana
* **Alerting:** Alertmanager, Slack API
* **DevOps & Infrastructure:** Docker, Docker Compose, GitHub Actions (CI/CD), AWS EC2 (Ubuntu)

---

## 🚀 API Endpoints
The inference API provides the following core endpoints, fully documented via an automated Swagger UI (`/docs`):

* `GET /health`: Lightweight health check endpoint to verify container uptime and simulate high-volume user traffic.
* `POST /predict`: The primary inference endpoint. Accepts a JSON payload containing a 2-feature array and returns the model's prediction.
  ```json
  // Request
  {
    "features": [0.5, 1.2]
  }
  // Response
  {
    "prediction": 1
  }
  ```
* `GET /force-alerts`: A specialized testing endpoint (tripwire) designed to manually trigger failure conditions, simulate DataLake connection drops, and force Alertmanager to route notifications to Slack.

---

## 📊 Observability & Metrics Tracking
The Prometheus and Grafana stack is pre-configured to monitor specific custom metrics critical to MLOps environments:
* **Ingestion Rate:** Tracks the volume of successful ML predictions over time.
* **P95 Latency:** Monitors server response times to detect performance bottlenecks during traffic spikes.
* **DataLake Availability:** Tracks infrastructure connection errors.
* **Data Drift Detection:** Identifies anomalous incoming data that deviates from the model's training baseline.

---

## ⚙️ Local Setup & Installation

To run this pipeline locally, ensure you have Docker and Docker Compose installed on your machine.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/automated-model-monitoring-system.git](https://github.com/your-username/automated-model-monitoring-system.git)
   cd automated-model-monitoring-system
   ```

2. **Configure Environment Variables:**
   Update the `alertmanager/alertmanager.yml` file with your specific Slack Webhook URL to enable incident routing.

3. **Spin up the containers:**
   ```bash
   docker compose up -d
   ```

4. **Access the Services:**
   * FastAPI Swagger UI: `http://localhost:8000/docs`
   * Prometheus Targets: `http://localhost:9090/targets`
   * Grafana Dashboard: `http://localhost:3000`

---

## 🔄 CI/CD & Deployment
This project utilizes **GitHub Actions** for Continuous Integration and Continuous Deployment. Upon every push to the `main` branch, the pipeline automatically:
1. Provisions an Ubuntu runner.
2. Checks out the latest codebase.
3. Securely authenticates with the target AWS EC2 instance via SSH keys.
4. Pulls the latest code, tears down the old Docker containers, and spins up the updated environment with zero manual intervention.
