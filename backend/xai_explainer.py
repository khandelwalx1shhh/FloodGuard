import torch
import lime
import lime.lime_tabular
import numpy as np
import pandas as pd
from data_preprocessing import load_and_preprocess_data
from rl_threat_scorer import ThreatScoringDQN  # Add this import
from sklearn.preprocessing import MinMaxScaler

class DDoSExplainer:
    def __init__(self, model_path):
        # Load the model architecture and state dict
        checkpoint = torch.load(model_path)
        self.model = ThreatScoringDQN(state_size=19, action_size=4)  # Initialize model architecture
        self.model.load_state_dict(checkpoint['dqn_state_dict'])
        self.model.eval()
        
        # Initialize feature names
        self.feature_names = [
            'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
            'Fwd Packets Length Total', 'Bwd Packets Length Total',
            'Fwd Packet Length Max', 'Fwd Packet Length Min',
            'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min',
            'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min',
            'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min'
        ]
        
        # Initialize LIME explainer
        X_train, _, _, _, _ = load_and_preprocess_data()
        self.explainer = lime.lime_tabular.LimeTabularExplainer(
            X_train.values,
            feature_names=self.feature_names,
            class_names=['Benign', 'DDoS'],
            mode='classification'
        )
    
    def predict_fn(self, input_data):
        input_tensor = torch.FloatTensor(input_data)
        with torch.no_grad():
            output = self.model(input_tensor)
            # Ensure proper probability distribution
            probabilities = torch.nn.functional.softmax(output, dim=1)
            # Convert to numpy and ensure valid probabilities
            probs = probabilities.numpy()
            # Normalize to ensure sum to 1
            probs = probs / np.sum(probs, axis=1, keepdims=True)
            # Replace any NaN values with 0.5 (neutral prediction)
            probs = np.nan_to_num(probs, nan=0.5)
            return probs
    
    def explain_prediction(self, input_data):
        # Normalize input data using min-max scaling
        scaler = MinMaxScaler()
        normalized_data = pd.DataFrame(
            scaler.fit_transform(input_data),
            columns=input_data.columns
        )
        
        # Generate LIME explanation
        explanation = self.explainer.explain_instance(
            normalized_data.iloc[0].values, 
            self.predict_fn,
            num_features=10,
            num_samples=500
        )
        
        # Get prediction
        pred = self.predict_fn(normalized_data.values)
        
        return {
            'feature_importance': dict(explanation.as_list()),
            'prediction': pred[0],
            'timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }