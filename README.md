# 🛡️ FloodGuard — DDoS Detection & Mitigation System

### 🚀 Advanced Network Security with Real-Time Monitoring

---

## 📌 Overview

**FloodGuard** is a cybersecurity system designed to detect and mitigate Distributed Denial of Service (DDoS) attacks through intelligent traffic analysis and real-time monitoring.

It combines machine learning techniques, network traffic analysis, and interactive visualization to identify abnormal patterns and respond to large-scale network attacks efficiently.

---

## 🧠 Key Features

* ⚡ Real-time network traffic monitoring
* 📊 Interactive visualization dashboard
* 🎯 Threat scoring and classification
* 🔍 Anomaly detection using ML models
* 🌐 Packet-level attack simulation
* 📈 Graph-based traffic analysis

---

## 🏗️ System Architecture

### 🔙 Backend

* Python-based analytics engine
* Handles data processing, detection logic, and ML models

### 🎨 Frontend

* React-based interface for visualization
* Uses D3.js for dynamic graphs and charts

### 🤖 Detection Models

* **Autoencoder** → Detects anomalies in traffic
* **Graph Neural Network (GNN)** → Analyzes network relationships
* **Reinforcement Learning** → Threat scoring
* **Explainable AI** → Provides decision insights

---

## ⚙️ Tech Stack

**Python, Machine Learning, Autoencoders, GNN, Reinforcement Learning, React.js, D3.js, Node.js, REST APIs**

---

## 🚀 Getting Started

### 🔧 Backend Setup

```bash id="a1b9c3"
cd backend
pip install -r requirements.txt
python data_preprocessing.py
```

---

### ▶️ Run Backend

```bash id="k9l2m1"
python app.py
```

---

### 📊 Launch Dashboard

```bash id="u3x0op"
python dashboard_v3.py
```

Access at:
👉 http://localhost:5000

---

### 🎨 Frontend Setup

```bash id="p9zm21"
cd frontendsim
npm install
npm run dev
```

Access at:
👉 http://localhost:5173

---

### 🔥 Attack Simulation

```bash id="t2djsk"
node server.js
```

---

## 📡 System Capabilities

* Detects abnormal traffic behavior
* Classifies DDoS attack patterns
* Assigns dynamic threat scores
* Provides insights into attack behavior
* Visualizes traffic data in real time
* Simulates attack scenarios for testing

---

## 📁 Project Structure

```id="z3a1bc"
FloodGuard/
├── backend/
│   ├── app.py
│   ├── autoencoder_model.py
│   ├── gnn_model.py
│   ├── rl_threat_scorer.py
│   ├── xai_explainer.py
│   └── dashboard_v3.py
├── frontendsim/
│   ├── React UI
│   ├── D3 Visualizations
│   └── Simulation Server
├── requirements.txt
└── README.md
```

---

## 🧪 Core Modules

* **Autoencoder Model** → Detects anomalies in traffic patterns
* **GNN Model** → Performs graph-based traffic analysis
* **RL Threat Scorer** → Assigns risk scores dynamically
* **XAI Explainer** → Explains model decisions

---

## 🔒 Security Capabilities

* Real-time anomaly detection
* Intelligent attack classification
* Adaptive threat scoring
* Simulation-based testing environment

---

## 🎯 Purpose

This project is built for **educational and cybersecurity research purposes**, demonstrating how modern systems detect and mitigate DDoS attacks.

---

## ⭐ Conclusion

FloodGuard represents a modern approach to network security by combining intelligent detection, real-time monitoring, and interactive visualization to effectively defend against DDoS attacks.

---

## 👨‍💻 Developer

**Vansh Khandelwal**

---
