# FloodGuard Backend

A machine learning-based backend system for detecting and analyzing Distributed Denial of Service (DDoS) attacks.

---

## Overview

The FloodGuard backend provides APIs for real-time network traffic analysis, attack detection, and data visualization. It integrates multiple machine learning models such as Graph Neural Networks (GNN) and Autoencoders to identify abnormal traffic patterns and potential DDoS attacks.

---

## Technology Stack

Python, Flask, Dash, PyTorch, Socket.IO, pandas, numpy

---

## Project Structure

```
backend/
├── app.py                 # Main application and API endpoints
├── data_preprocessing.py  # Data cleaning and preparation
├── gnn_model.py           # Graph Neural Network model
├── autoencoder_model.py   # Anomaly detection model
├── train_models.py        # Model training scripts
├── xai_explainer.py       # Explainable AI logic
├── data_provider_v3.py    # Data simulation and processing
└── templates/             # Dashboard templates
```

---

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Train Models

```bash
python train_models.py
```

---

### 4. Run Application

```bash
python app.py
```

---

## API Endpoints

| Endpoint                | Method | Description                  |
| ----------------------- | ------ | ---------------------------- |
| `/api/attack-data`      | GET    | Latest attack detection data |
| `/api/network-data`     | GET    | Network visualization data   |
| `/api/historical-data`  | GET    | Historical attack data       |
| `/api/model-prediction` | POST   | Model prediction for traffic |
| `/health`               | GET    | Service health status        |

---

## Model Components

### Graph Neural Network (GNN)

* Analyzes network structure and traffic flow
* Detects distributed attack patterns

### Autoencoder

* Learns normal traffic behavior
* Identifies anomalies and unusual spikes

### Explainable AI (XAI)

* Provides insights into model decisions
* Improves transparency of detection results

---

## Features

* Real-time traffic monitoring
* Machine learning-based anomaly detection
* API-driven architecture
* Scalable backend design
* Support for simulation and testing

---

## Purpose

This backend is developed for educational and cybersecurity research purposes, focusing on detection and analysis of DDoS attacks.

---

## Developer

Vansh Khandelwal

---
