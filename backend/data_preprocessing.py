import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os
import glob

def load_and_preprocess_data(sample_size=100000):
    # Define the path to the dataset directory
    dataset_dir = r"d:\CyberProject\V2\backend\dataset_ddos2019"
    
    # Check if the directory exists
    if not os.path.exists(dataset_dir):
        print(f"Dataset directory not found at {dataset_dir}")
        return None, None, None, None, None
    
    # Find all CSV files in the directory
    csv_files = glob.glob(os.path.join(dataset_dir, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {dataset_dir}")
        return None, None, None, None, None
    
    # Define the columns we want to read (updated to match actual CSV columns)
    features = [
        'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
        'Fwd Packets Length Total', 'Bwd Packets Length Total',
        'Fwd Packet Length Max', 'Fwd Packet Length Min',
        'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min',
        'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min',
        'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min',
        'Label'
    ]

    # Process all CSV files and combine them
    all_data = []
    for file_index, dataset_path in enumerate(csv_files):
        print(f"\nProcessing file {file_index + 1}/{len(csv_files)}: {os.path.basename(dataset_path)}")
        
        # Calculate sampling rate for this file
        total_lines = sum(1 for _ in open(dataset_path, 'r'))
        sampling_rate = (sample_size / len(csv_files)) / (total_lines - 1)
        
        # Load a sample from current CSV
        df = pd.read_csv(
            dataset_path,
            usecols=features,
            skiprows=lambda i: i > 0 and np.random.random() > sampling_rate,
            low_memory=False
        )
        all_data.append(df)
        print(f"Loaded {len(df)} samples from {os.path.basename(dataset_path)}")
    
    # Combine all dataframes
    df = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal samples after combining all files: {len(df)}")
    
    # Separate features and target
    X = df.drop('Label', axis=1)
    y = df['Label']
    
    # Handle missing values
    X = X.fillna(X.mean())
    
    # Feature scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    return X_train, X_test, y_train, y_test, scaler

if __name__ == "__main__":
    try:
        X_train, X_test, y_train, y_test, scaler = load_and_preprocess_data()
        
        if X_train is not None:
            print("\nData preprocessing completed successfully!")
            print(f"Training set shape: {X_train.shape}")
            print(f"Testing set shape: {X_test.shape}")
            
            # Print unique attack types in the dataset
            print("\nUnique attack types in the dataset:")
            print(pd.concat([y_train, y_test]).unique())
    except Exception as e:
        print(f"Error during data preprocessing: {str(e)}")