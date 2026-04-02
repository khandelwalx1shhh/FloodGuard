# DDoS.AI - Advanced DDoS Detection and Mitigation System

An intelligent system for detecting and mitigating Distributed Denial of Service (DDoS) attacks using AI-powered models for real-time analysis and visualization.

## Project Overview

This project combines machine learning techniques with network traffic analysis to identify and mitigate DDoS attacks. The system consists of:

- **Backend**: Python-based analytics engine with machine learning models
- **Frontend**: Interactive visualization and simulation dashboard

## Getting Started

### Prerequisites

#### Backend

- Python 3.8+
- Required Python libraries (see requirements.bat)
- Sufficient RAM for ML model training (8GB+ recommended)

#### Frontend

- Node.js 14+
- npm or yarn

### Installation

#### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Install required dependencies:

   ```bash
   ./requirements.bat
   ```

   or

   ```bash
   pip install -r requirements.txt
   ```

3. Prepare dataset (if needed):
   ```bash
   python data_preprocessing.py
   ```

#### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontendsim
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Usage

### Running the Backend

1. Start the main application:

   ```bash
   cd backend
   python app.py
   ```

2. Launch the dashboard (in a separate terminal):
   ```bash
   python dashboard_v3.py
   ```
   The dashboard will be available at http://localhost:5000

### Running the Frontend

1. Start the development server:

   ```bash
   cd frontendsim
   npm run dev
   ```

   Access the frontend at http://localhost:5173

2. For production build:

   ```bash
   npm run build
   ```

3. To simulate packet attacks on the frontend:
   ```bash
   cd frontendsim
   node server.js
   ```
   This will start the attack simulation server that generates packet data for visualization and testing.

### System Capabilities

- Real-time network traffic monitoring
- Anomaly detection using autoencoders
- Graph-based traffic analysis with GNN
- Threat scoring and classification
- Explainable AI for decision insights
- Interactive traffic simulation
- Visual analytics dashboard

## Project Structure

### Backend Components

- app.py - Main application entry point
- autoencoder_model.py - Anomaly detection
- gnn_model.py - Graph neural network analysis
- rl_threat_scorer.py - Reinforcement learning scoring
- xai_explainer.py - Explainable AI component
- dashboard_v3.py - Visualization dashboard

### Frontend Components

- React-based user interface
- D3.js visualizations
- Network simulation environment
- Real-time monitoring panels

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
