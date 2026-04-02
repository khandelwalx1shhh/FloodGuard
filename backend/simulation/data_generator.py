import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import random
import json
import logging
import os
from utils.helpers import json_serialize_fix

logger = logging.getLogger(__name__)

# Constants
ATTACK_TYPES = {
    'SYN Flood': {'color': '#FF5733', 'threshold': 0.7},
    'HTTP Flood': {'color': '#33A8FF', 'threshold': 0.65},
    'UDP Flood': {'color': '#FF33A8', 'threshold': 0.75},
    'Slowloris': {'color': '#A833FF', 'threshold': 0.6},
    'DNS Amplification': {'color': '#33FFA8', 'threshold': 0.8}
}

THREAT_LEVELS = {
    'Low': (0, 0.4, '#92D050'),
    'Medium': (0.4, 0.7, '#FFC000'),
    'High': (0.7, 0.9, '#FF0000'),
    'Critical': (0.9, 1.0, '#7030A0')
}

def get_threat_level(probability):
    """Return the threat level based on probability"""
    for level, (min_val, max_val, _) in THREAT_LEVELS.items():
        if min_val <= probability < max_val:
            return level
    return 'Critical'

def get_threat_color(probability):
    """Return the color code for a threat level"""
    for _, (min_val, max_val, color) in THREAT_LEVELS.items():
        if min_val <= probability < max_val:
            return color
    return THREAT_LEVELS['Critical'][2]

def generate_initial_data(hours=24):
    """Generate initial synthetic data for the dashboard"""
    base = datetime.now() - timedelta(hours=hours)
    data = {
        'timestamp': [],
        'traffic': [],
        'attack_probability': [],
        'attack_type': [],
        'blocked_requests': []
    }
    
    for i in range(hours * 12):  # 5-minute intervals
        current_time = base + timedelta(minutes=i*5)
        
        # Normal traffic pattern with some randomness
        hour_of_day = current_time.hour
        # Traffic follows a typical day/night pattern
        base_traffic = 50 + 50 * np.sin(np.pi * hour_of_day / 12)
        
        # Add some randomness
        traffic = max(10, base_traffic + random.normalvariate(0, 10))
        
        # Generate attack probability - mostly low but occasional spikes
        attack_prob = random.betavariate(0.2, 2.0) if random.random() > 0.8 else random.betavariate(0.1, 10.0)
        
        # Determine attack type based on probability
        attack_type = 'Normal'
        if attack_prob > 0.5:
            weights = [ATTACK_TYPES[t]['threshold'] for t in ATTACK_TYPES]
            attack_type = random.choices(list(ATTACK_TYPES.keys()), weights=weights, k=1)[0]
        
        # Blocked requests correlated with attack probability
        blocked = int(attack_prob * traffic * 0.8) if attack_prob > 0.5 else int(random.random() * traffic * 0.05)
        
        # Add to our dataset
        data['timestamp'].append(current_time)
        data['traffic'].append(traffic)
        data['attack_probability'].append(attack_prob)
        data['attack_type'].append(attack_type)
        data['blocked_requests'].append(blocked)
    
    return pd.DataFrame(data)

def simulate_ddos(socketio):
    """
    Continuously simulate DDoS attack data and emit updates via WebSockets.
    """
    logger.info("Starting DDoS simulation thread")
    df = generate_initial_data(hours=24)
    
    # Save historical data initially
    records = []
    for _, row in df.iterrows():
        record = {
            'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'traffic': float(row['traffic']),
            'attack_probability': float(row['attack_probability']),
            'attack_type': row['attack_type'],
            'blocked_requests': int(row['blocked_requests'])
        }
        records.append(record)
    
    with open('historical_data.json', 'w') as f:
        json.dump(records, f, default=json_serialize_fix)
    
    while True:
        try:
            # Add new data point (simulating real-time)
            last_time = df['timestamp'].iloc[-1]
            new_time = last_time + timedelta(minutes=5)
            
            # Determine if we're in an attack period
            # Higher probability of attack during business hours
            hour_of_day = new_time.hour
            is_business_hours = 9 <= hour_of_day <= 17
            attack_period = random.random() < (0.2 if is_business_hours else 0.05)
            
            if attack_period:
                attack_prob = random.uniform(0.6, 0.95)
                traffic = random.uniform(100, 300)
                attack_choices = list(ATTACK_TYPES.keys())
                weights = [ATTACK_TYPES[t]['threshold'] for t in attack_choices]
                attack_type = random.choices(attack_choices, weights=weights, k=1)[0]
                blocked = int(attack_prob * traffic * 0.8)
            else:
                base_traffic = 50 + 50 * np.sin(np.pi * hour_of_day / 12)
                traffic = max(10, base_traffic + random.normalvariate(0, 10))
                attack_prob = random.betavariate(0.1, 10.0)
                attack_type = 'Normal'
                blocked = int(random.random() * traffic * 0.05)
            
            # Create new row
            new_row = pd.DataFrame({
                'timestamp': [new_time],
                'traffic': [traffic],
                'attack_probability': [attack_prob],
                'attack_type': [attack_type],
                'blocked_requests': [blocked]
            })
            
            # Append and maintain window
            df = pd.concat([df.iloc[1:], new_row], ignore_index=True)
            
            # Update historical data
            records = []
            for _, row in df.iterrows():
                record = {
                    'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(row['timestamp'], datetime) else row['timestamp'],
                    'traffic': float(row['traffic']),
                    'attack_probability': float(row['attack_probability']),
                    'attack_type': row['attack_type'],
                    'blocked_requests': int(row['blocked_requests'])
                }
                records.append(record)
            
            with open('historical_data.json', 'w') as f:
                json.dump(records, f, default=json_serialize_fix)
            
            # Emit the data
            threat_level = get_threat_level(attack_prob)
            threat_color = get_threat_color(attack_prob)
            
            socketio.emit('ddos_update', {
                'time': new_time.strftime('%Y-%m-%d %H:%M:%S'),
                'traffic': traffic,
                'attack_probability': attack_prob,
                'attack_type': attack_type if attack_type != 'Normal' else None,
                'blocked_requests': blocked,
                'threat_level': threat_level,
                'threat_color': threat_color
            })
            
            # Also save the latest state for API access
            latest_data = {
                'timestamp': new_time.strftime('%Y-%m-%d %H:%M:%S'),
                'traffic_level': traffic,
                'attack_probability': attack_prob,
                'attack_type': attack_type if attack_type != 'Normal' else None,
                'blocked_requests': blocked,
                'threat_level': threat_level
            }
            
            with open('latest_attack_data.json', 'w') as f:
                json.dump(latest_data, f, default=json_serialize_fix)
            
            # Sleep for longer (5 seconds) to match UI refresh rate
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error in simulation thread: {e}")
            time.sleep(2)  # Wait and try again