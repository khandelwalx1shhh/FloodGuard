# DDoS.AI Backend

A machine learning-powered DDoS detection and mitigation system.

## Overview

The backend provides a robust API for real-time traffic analysis, attack detection, and visualization. It integrates multiple AI models including Graph Neural Networks (GNN) and Autoencoders for comprehensive protection.

## Technology Stack

- Python 3.8+
- Flask/Dash for web server and dashboard
- PyTorch for ML models
- Socket.IO for real-time communication
- pandas/numpy for data processing

## Project Structure

```
backend/
├── app.py                 # Main Flask application and API endpoints
├── data_preprocessing.py  # Data cleaning and preparation
├── gnn_model.py           # Graph Neural Network implementation
├── autoencoder_model.py   # Autoencoder model for anomaly detection
├── train_models.py        # Scripts for model training
├── xai_explainer.py       # Explainable AI components
├── data_provider_v3.py    # Data simulation and processing
└── templates/             # HTML templates
```

## Setup Instructions

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Train the models:

```bash
python train_models.py
```

4. Start the application:

```bash
python app.py
```

## API Endpoints

| Endpoint                | Method | Description                            |
| ----------------------- | ------ | -------------------------------------- |
| `/api/attack-data`      | GET    | Get latest attack detection data       |
| `/api/network-data`     | GET    | Get network visualization data         |
| `/api/historical-data`  | GET    | Get historical attack data             |
| `/api/model-prediction` | POST   | Get model predictions for traffic data |
| `/health`               | GET    | Service health check                   |

## Model Architecture

### Graph Neural Network (GNN)

- Analyzes traffic patterns and network topology
- Detects distributed attacks by understanding network relationships

### Autoencoder

- Identifies anomalies in network traffic
- Learns normal traffic patterns and flags deviations

## Contributing

Please follow our coding standards when contributing:

1. Use type hints for all function definitions
2. Add docstrings for all functions and classes
3. Write unit tests for new functionality

## License

This project is proprietary software. All rights reserved.
