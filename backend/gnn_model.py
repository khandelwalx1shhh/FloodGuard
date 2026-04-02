import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data, Dataset
import pandas as pd
import numpy as np
from data_preprocessing import load_and_preprocess_data

class TrafficGNN(torch.nn.Module):
    def __init__(self, num_features, hidden_channels, num_classes):
        super(TrafficGNN, self).__init__()
        self.conv1 = GCNConv(num_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, num_classes)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        
        x = self.conv3(x, edge_index)
        return F.log_softmax(x, dim=1)

def create_graph_data(X, y, k=10):
    # Convert features to node features
    x = torch.FloatTensor(X.values)
    
    # Create edge index using k-nearest neighbors instead of fully connected
    # This significantly reduces memory usage
    num_nodes = len(X)
    edge_index = []
    
    # Use batch processing to avoid memory issues
    batch_size = 1000
    for start_idx in range(0, num_nodes, batch_size):
        end_idx = min(start_idx + batch_size, num_nodes)
        batch_nodes = X.iloc[start_idx:end_idx]
        
        # For each node in the batch, connect to k random nodes
        for i in range(start_idx, end_idx):
            # Select k random connections
            random_connections = np.random.choice(
                num_nodes, 
                size=min(k, num_nodes-1), 
                replace=False
            )
            
            # Remove self-connection if present
            random_connections = random_connections[random_connections != i]
            
            # Add edges
            for j in random_connections:
                edge_index.append([i, j])
    
    edge_index = torch.LongTensor(edge_index).t()
    
    # Convert labels to tensor
    y = torch.LongTensor(pd.Categorical(y).codes)
    
    return Data(x=x, edge_index=edge_index, y=y)

def train_gnn_model(max_samples=10000):
    # Load preprocessed data
    X_train, X_test, y_train, y_test, _ = load_and_preprocess_data()
    
    if X_train is None:
        return None
    
    # Limit the number of samples to avoid memory issues
    if len(X_train) > max_samples:
        print(f"Limiting training samples from {len(X_train)} to {max_samples}")
        X_train = X_train.sample(max_samples, random_state=42)
        y_train = y_train.loc[X_train.index]
    
    if len(X_test) > max_samples // 4:
        X_test = X_test.sample(max_samples // 4, random_state=42)
        y_test = y_test.loc[X_test.index]
    
    print(f"Creating graph with {len(X_train)} training nodes and {len(X_test)} testing nodes")
    
    # Create graph data
    train_data = create_graph_data(X_train, y_train)
    test_data = create_graph_data(X_test, y_test)
    
    # Initialize model
    model = TrafficGNN(
        num_features=X_train.shape[1],
        hidden_channels=64,
        num_classes=len(np.unique(y_train))
    )
    
    # Training settings
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    criterion = torch.nn.NLLLoss()
    
    # Training loop
    model.train()
    for epoch in range(100):
        optimizer.zero_grad()
        out = model(train_data.x, train_data.edge_index)
        loss = criterion(out, train_data.y)
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 10 == 0:
            print(f'Epoch {epoch+1:03d}, Loss: {loss:.4f}')
    
    # Evaluation
    model.eval()
    with torch.no_grad():
        pred = model(test_data.x, test_data.edge_index)
        pred = pred.argmax(dim=1)
        correct = (pred == test_data.y).sum()
        acc = int(correct) / len(test_data.y)
        print(f'Accuracy: {acc:.4f}')
    
    return model

if __name__ == "__main__":
    model = train_gnn_model()
    if model is not None:
        # Save the model
        torch.save(model.state_dict(), r"d:\CyberProject\V2\backend\models\traffic_gnn.pt")