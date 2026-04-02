import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.metrics import precision_recall_curve
from data_preprocessing import load_and_preprocess_data

class TrafficAutoencoder(nn.Module):
    def __init__(self, input_dim):
        super(TrafficAutoencoder, self).__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim),
            nn.Sigmoid()
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

def train_autoencoder(max_samples=100000):
    # Load preprocessed data
    X_train, X_test, y_train, y_test, _ = load_and_preprocess_data()
    
    if X_train is None:
        return None, None
    
    # Convert to PyTorch tensors
    X_train_tensor = torch.FloatTensor(X_train.values)
    X_test_tensor = torch.FloatTensor(X_test.values)
    
    # Initialize model and training parameters
    model = TrafficAutoencoder(input_dim=X_train.shape[1])
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    n_epochs = 50
    batch_size = 256
    
    for epoch in range(n_epochs):
        model.train()
        total_loss = 0
        
        # Train in batches
        for i in range(0, len(X_train_tensor), batch_size):
            batch = X_train_tensor[i:i+batch_size]
            
            # Forward pass
            output = model(batch)
            loss = criterion(output, batch)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        if (epoch + 1) % 5 == 0:
            print(f'Epoch [{epoch+1}/{n_epochs}], Loss: {total_loss/len(X_train_tensor):.6f}')
    
    # Find optimal threshold using validation set
    model.eval()
    with torch.no_grad():
        test_output = model(X_test_tensor)
        reconstruction_errors = torch.mean((X_test_tensor - test_output) ** 2, dim=1).numpy()
        
        # Convert labels to binary (DDoS = 1, Benign = 0)
        y_test_binary = np.where(y_test != 'BENIGN', 1, 0)
        
        # Find optimal threshold using precision-recall curve
        precisions, recalls, thresholds = precision_recall_curve(y_test_binary, reconstruction_errors)
        f1_scores = 2 * (precisions * recalls) / (precisions + recalls)
        optimal_threshold = thresholds[np.argmax(f1_scores[:-1])]
        
        print(f"\nOptimal threshold: {optimal_threshold:.6f}")
        
        # Evaluate performance
        predictions = (reconstruction_errors > optimal_threshold).astype(int)
        accuracy = np.mean(predictions == y_test_binary)
        print(f"Detection accuracy: {accuracy:.4f}")
    
    return model, optimal_threshold

if __name__ == "__main__":
    model, threshold = train_autoencoder()
    if model is not None:
        # Save the model and threshold
        torch.save({
            'model_state_dict': model.state_dict(),
            'threshold': threshold
        }, r"d:\CyberProject\V2\backend\models\traffic_autoencoder.pt")