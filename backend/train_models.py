import torch
import torch.nn as nn
from autoencoder_model import TrafficAutoencoder
from gnn_model import TrafficGNN
from data_preprocessing import load_and_preprocess_data
import os

# Create models directory if it doesn't exist
os.makedirs(r"d:\CyberProject\V2\backend\models", exist_ok=True)

# Load and preprocess data
X_train, X_test, y_train, y_test, feature_names = load_and_preprocess_data()

# Convert labels to numeric values (0 for benign, 1 for attack)
y_train_numeric = (y_train == 'attack').astype(int).values  # Add .values
y_test_numeric = (y_test == 'attack').astype(int).values    # Add .values

# Convert to tensors
X_train_tensor = torch.FloatTensor(X_train.values)
X_test_tensor = torch.FloatTensor(X_test.values)
y_train_tensor = torch.LongTensor(y_train_numeric)
y_test_tensor = torch.LongTensor(y_test_numeric)

# Train Autoencoder
print("Training Autoencoder...")
autoencoder = TrafficAutoencoder(input_dim=19)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(autoencoder.parameters(), lr=0.001)

for epoch in range(50):
    optimizer.zero_grad()
    outputs = autoencoder(X_train_tensor)
    loss = criterion(outputs, X_train_tensor)
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 10 == 0:
        print(f'Epoch [{epoch+1}/50], Loss: {loss.item():.4f}')

# Save Autoencoder (state dict only)
torch.save(autoencoder.state_dict(), r"d:\CyberProject\V2\backend\models\traffic_autoencoder.pt", _use_new_zipfile_serialization=True)

# Train GNN
print("\nTraining GNN...")
gnn_model = TrafficGNN(num_features=19, hidden_channels=64, num_classes=2)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(gnn_model.parameters(), lr=0.001)

edge_index = torch.tensor([[i for i in range(len(X_train))], 
                          [i for i in range(len(X_train))]], dtype=torch.long)

for epoch in range(50):
    optimizer.zero_grad()
    outputs = gnn_model(X_train_tensor, edge_index)
    loss = criterion(outputs, y_train_tensor)
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 10 == 0:
        print(f'Epoch [{epoch+1}/50], Loss: {loss.item():.4f}')

# Save GNN (state dict only)
torch.save(gnn_model.state_dict(), r"d:\CyberProject\V2\backend\models\traffic_gnn_model.pt", _use_new_zipfile_serialization=True)

print("\nModel training completed and saved!")