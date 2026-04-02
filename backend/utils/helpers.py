import numpy as np
import pandas as pd
from datetime import datetime

def json_serialize_fix(obj):
    """
    Helper function to make NumPy data types JSON serializable
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return obj

def get_threat_level(probability):
    """Get threat level based on probability"""
    if probability < 0.4:
        return "Low"
    elif probability < 0.7:
        return "Medium"
    elif probability < 0.9:
        return "High"
    else:
        return "Critical"

def get_threat_color(probability):
    """Get color code for threat level"""
    if probability < 0.4:
        return "#92D050"  # Green
    elif probability < 0.7:
        return "#FFC000"  # Yellow
    elif probability < 0.9:
        return "#FF0000"  # Red
    else:
        return "#7030A0"  # Purple