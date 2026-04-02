import pandas as pd
import numpy as np
import json
import os
import logging
from datetime import datetime, timedelta
import random
import requests
from typing import Dict, List, Union, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)

# File path for storing latest attack data
DATA_FILE_PATH = 'latest_attack_data.json'

# Constants for threat levels (same as in dashboard_v3.py)
THREAT_LEVELS = {
    'Low': (0, 0.4, '#92D050'),
    'Medium': (0.4, 0.7, '#FFC000'),
    'High': (0.7, 0.9, '#FF0000'),
    'Critical': (0.9, 1.0, '#7030A0')
}

# Attack types (same as in dashboard_v3.py)
ATTACK_TYPES = {
    'SYN Flood': {'color': '#FF5733', 'threshold': 0.7},
    'HTTP Flood': {'color': '#33A8FF', 'threshold': 0.65},
    'UDP Flood': {'color': '#FF33A8', 'threshold': 0.75},
    'Slowloris': {'color': '#A833FF', 'threshold': 0.6},
    'DNS Amplification': {'color': '#33FFA8', 'threshold': 0.8}
}

def json_serialize_fix(obj):
    """
    Helper function to make NumPy data types JSON serializable
    """
    import numpy as np
    
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return obj

def get_threat_level(probability: float) -> str:
    """
    Determine threat level based on probability.
    
    Args:
        probability: Attack probability value between 0 and 1
        
    Returns:
        String representation of the threat level
    """
    for level, (min_val, max_val, _) in THREAT_LEVELS.items():
        if min_val <= probability < max_val:
            return level
    return 'Critical'

def get_threat_color(probability: float) -> str:
    """
    Get the color associated with a threat level.
    
    Args:
        probability: Attack probability value between 0 and 1
        
    Returns:
        Hex color code for the threat level
    """
    for _, (min_val, max_val, color) in THREAT_LEVELS.items():
        if min_val <= probability < max_val:
            return color
    return THREAT_LEVELS['Critical'][2]

def generate_attack_data(hours: int = 24) -> pd.DataFrame:
    """
    Generate synthetic DDoS attack data for a specified time period.
    
    Args:
        hours: Number of hours of data to generate
    
    Returns:
        DataFrame with attack data
    """
    base = datetime.now() - timedelta(hours=hours)
    data = {
        'timestamp': [],
        'traffic': [],
        'attack_probability': [],
        'attack_type': [],
        'blocked_requests': [],
        'source_ips': [],
        'target_services': []
    }
    
    # Common services that might be targeted
    target_services = ['Web Server', 'DNS', 'API Gateway', 'Database', 'Authentication Service']
    
    for i in range(hours * 12):  # 5-minute intervals
        current_time = base + timedelta(minutes=i*5)
        
        # Normal traffic pattern with some randomness
        hour_of_day = current_time.hour
        # Traffic follows a typical day/night pattern
        base_traffic = 50 + 50 * np.sin(np.pi * hour_of_day / 12)
        
        # Add some randomness
        traffic = max(10, base_traffic + random.normalvariate(0, 10))
        
        # Generate attack probability - mostly low but occasional spikes
        is_attack = random.random() > 0.85  # 15% chance of attack
        attack_prob = random.uniform(0.6, 0.95) if is_attack else random.betavariate(0.1, 10.0)
        
        # Determine attack type based on probability
        attack_type = 'Normal'
        if attack_prob > 0.5:
            weights = [ATTACK_TYPES[t]['threshold'] for t in ATTACK_TYPES]
            attack_type = random.choices(list(ATTACK_TYPES.keys()), weights=weights, k=1)[0]
        
        # Blocked requests correlated with attack probability
        blocked = int(attack_prob * traffic * 0.8) if attack_prob > 0.5 else int(random.random() * traffic * 0.05)
        
        # Generate source IPs
        num_source_ips = int(traffic / 10) + 1
        if attack_prob > 0.5:  # If under attack, fewer source IPs (more concentrated)
            num_source_ips = max(1, int(num_source_ips / 3))
        
        source_ips = [f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}" for _ in range(num_source_ips)]
        
        # Targeted service
        target_service = random.choice(target_services)
        
        # Add to our dataset
        data['timestamp'].append(current_time)
        data['traffic'].append(traffic)
        data['attack_probability'].append(attack_prob)
        data['attack_type'].append(attack_type)
        data['blocked_requests'].append(blocked)
        data['source_ips'].append(source_ips)
        data['target_services'].append(target_service)
    
    return pd.DataFrame(data)

def get_latest_attack_data() -> Dict[str, Any]:
    """
    Get the latest attack data from the data file or generate if not available.
    
    Returns:
        Dictionary containing latest attack data
    """
    try:
        if os.path.exists(DATA_FILE_PATH):
            with open(DATA_FILE_PATH, 'r') as f:
                data = json.load(f)
                
                # Check if data is fresh (less than 1 minute old)
                if 'timestamp' in data:
                    data_time = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
                    if datetime.now() - data_time < timedelta(minutes=1):
                        return data
        
        # If file doesn't exist or data is stale, generate new data
        df = generate_attack_data(hours=1)
        latest_row = df.iloc[-1]
        
        latest_data = {
            'timestamp': latest_row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'traffic_level': float(latest_row['traffic']),
            'attack_probability': float(latest_row['attack_probability']),
            'attack_type': latest_row['attack_type'] if latest_row['attack_type'] != 'Normal' else None,
            'blocked_requests': int(latest_row['blocked_requests']),
            'threat_level': get_threat_level(latest_row['attack_probability']),
            'threat_color': get_threat_color(latest_row['attack_probability']),
            'source_ips': latest_row['source_ips'],
            'target_service': latest_row['target_services']
        }
        
        # Save the data for future use
        with open(DATA_FILE_PATH, 'w') as f:
            json.dump(latest_data, f, default=json_serialize_fix)
        
        return latest_data
        
    except Exception as e:
        logger.error(f"Error getting latest attack data: {e}")
        # Return fallback data
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'traffic_level': 75.0,
            'attack_probability': 0.2,
            'attack_type': None,
            'blocked_requests': 5,
            'threat_level': 'Low',
            'threat_color': '#92D050',
            'source_ips': ['192.168.1.100', '192.168.1.101'],
            'target_service': 'Web Server'
        }

def get_historical_attack_data(hours: int = 24) -> pd.DataFrame:
    """
    Get historical attack data for visualization and analysis.
    
    Args:
        hours: Number of hours of data to retrieve
    
    Returns:
        DataFrame with historical attack data
    """
    try:
        # Try to load historical data from file first
        if os.path.exists('historical_data.json'):
            with open('historical_data.json', 'r') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                
                # Convert timestamp strings to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Filter for requested time period
                start_time = datetime.now() - timedelta(hours=hours)
                df = df[df['timestamp'] >= start_time]
                
                if not df.empty:
                    return df
        
        # If no historical data or filtered data is empty, generate synthetic data
        return generate_attack_data(hours=hours)
        
    except Exception as e:
        logger.error(f"Error getting historical attack data: {e}")
        # Return minimal data to prevent visualization errors
        base = datetime.now() - timedelta(hours=hours)
        data = {
            'timestamp': [base + timedelta(hours=i) for i in range(hours)],
            'traffic': [50.0] * hours,
            'attack_probability': [0.1] * hours,
            'attack_type': ['Normal'] * hours,
            'blocked_requests': [0] * hours,
            'source_ips': [[]] * hours,
            'target_services': ['Web Server'] * hours
        }
        return pd.DataFrame(data)

def get_attack_statistics() -> Dict[str, Any]:
    """
    Calculate statistics about recent attacks.
    
    Returns:
        Dictionary with attack statistics
    """
    try:
        df = get_historical_attack_data(hours=24)
        
        # Count attack occurrences by type
        attack_counts = df[df['attack_type'] != 'Normal']['attack_type'].value_counts().to_dict()
        
        # Calculate average traffic and blocked requests
        avg_traffic = df['traffic'].mean()
        total_blocked = df['blocked_requests'].sum()
        
        # Calculate peak attack probability
        peak_attack_prob = df['attack_probability'].max()
        peak_attack_time = df.loc[df['attack_probability'].idxmax(), 'timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Attack duration calculation (consecutive periods with probability > 0.5)
        attack_periods = []
        current_attack = {'start': None, 'end': None, 'duration': 0}
        
        for i, row in df.iterrows():
            if row['attack_probability'] > 0.5:
                if current_attack['start'] is None:
                    current_attack['start'] = row['timestamp']
                current_attack['end'] = row['timestamp']
            elif current_attack['start'] is not None:
                # Attack ended, calculate duration
                duration = (current_attack['end'] - current_attack['start']).total_seconds() / 60  # minutes
                attack_periods.append({
                    'start': current_attack['start'].strftime('%Y-%m-%d %H:%M:%S'),
                    'end': current_attack['end'].strftime('%Y-%m-%d %H:%M:%S'),
                    'duration_minutes': duration,
                    'max_probability': df[(df['timestamp'] >= current_attack['start']) & 
                                        (df['timestamp'] <= current_attack['end'])]['attack_probability'].max()
                })
                current_attack = {'start': None, 'end': None, 'duration': 0}
        
        # Check if we're still in an attack at the end of the data
        if current_attack['start'] is not None:
            duration = (current_attack['end'] - current_attack['start']).total_seconds() / 60  # minutes
            attack_periods.append({
                'start': current_attack['start'].strftime('%Y-%m-%d %H:%M:%S'),
                'end': current_attack['end'].strftime('%Y-%m-%d %H:%M:%S'),
                'duration_minutes': duration,
                'max_probability': df[(df['timestamp'] >= current_attack['start']) & 
                                     (df['timestamp'] <= current_attack['end'])]['attack_probability'].max()
            })
        
        return {
            'attack_counts': attack_counts,
            'total_attacks': len(attack_periods),
            'avg_traffic': avg_traffic,
            'total_blocked': total_blocked,
            'peak_attack': {
                'probability': peak_attack_prob,
                'time': peak_attack_time,
                'level': get_threat_level(peak_attack_prob)
            },
            'attack_periods': attack_periods,
            'current_status': get_latest_attack_data()
        }
        
    except Exception as e:
        logger.error(f"Error calculating attack statistics: {e}")
        return {
            'attack_counts': {},
            'total_attacks': 0,
            'avg_traffic': 0,
            'total_blocked': 0,
            'peak_attack': {
                'probability': 0,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'level': 'Low'
            },
            'attack_periods': [],
            'current_status': get_latest_attack_data()
        }

def get_network_data() -> Dict[str, Any]:
    """
    Get network-related data for visualization.
    
    Returns:
        Dictionary with network data
    """
    try:
        df = get_historical_attack_data(hours=6)
        
        # Extract unique source IPs
        all_ips = set()
        for ips in df['source_ips']:
            all_ips.update(ips)
        
        # Count requests by service
        service_counts = df['target_services'].value_counts().to_dict()
        
        # Create network graph data
        nodes = []
        edges = []
        
        # Add service nodes
        for service, count in service_counts.items():
            nodes.append({
                'id': service,
                'label': service,
                'type': 'service',
                'size': 20,
                'color': '#2980b9'
            })
        
        # Add IP nodes and connections
        for ip in list(all_ips)[:30]:  # Limit to 30 IPs for visualization
            nodes.append({
                'id': ip,
                'label': ip,
                'type': 'ip',
                'size': 10,
                'color': '#e74c3c' if random.random() > 0.7 else '#7f8c8d'  # Some IPs marked as suspicious
            })
            
            # Connect to random services with varying weights
            for service in random.sample(list(service_counts.keys()), k=min(3, len(service_counts))):
                edges.append({
                    'source': ip,
                    'target': service,
                    'value': random.randint(1, 10)
                })
        
        # Add firewall and server nodes for visualization
        nodes.append({
            'id': 'server',
            'label': 'Main Server',
            'type': 'server',
            'size': 25,
            'color': '#2196F3'
        })
        
        nodes.append({
            'id': 'firewall',
            'label': 'Firewall',
            'type': 'firewall',
            'size': 20,
            'color': '#4CAF50'
        })
        
        # Connect firewall to server
        edges.append({
            'source': 'firewall',
            'target': 'server',
            'value': 15,
            'label': 'Protected'
        })
        
        # Connect IPs to firewall
        for ip in list(all_ips)[:30]:
            is_blocked = random.random() < 0.3
            edges.append({
                'source': ip,
                'target': 'firewall',
                'value': random.randint(1, 10),
                'status': 'blocked' if is_blocked else 'allowed'
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'total_ips': len(all_ips),
            'service_counts': service_counts
        }
        
    except Exception as e:
        logger.error(f"Error getting network data: {e}")
        return {
            'nodes': [
                {'id': 'server', 'label': 'Main Server', 'size': 20, 'color': '#2196F3'},
                {'id': 'firewall', 'label': 'Firewall', 'size': 15, 'color': '#4CAF50'}
            ],
            'edges': [
                {'from': 'firewall', 'to': 'server', 'value': 10, 'label': 'Protected', 'color': '#4CAF50'}
            ],
            'total_ips': 0,
            'service_counts': {}
        }

def integrate_model_predictions(traffic_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integrate predictions from the V3 ML models with traffic data.
    
    Args:
        traffic_data: Current traffic data
    
    Returns:
        Enhanced data with model predictions
    """
    try:
        # This would make an API call to the ML models in a real implementation
        # For now, we'll simulate the result
        
        # Convert traffic_data to the format expected by the models
        model_input = {
            'model_type': 'rl',  # Default to RL model
            'flow_duration': random.uniform(0.5, 3.0),
            'total_fwd_packets': traffic_data.get('traffic_level', 75) / 10,
            'total_backward_packets': traffic_data.get('traffic_level', 75) / 15,
            'fwd_packets_length_total': traffic_data.get('traffic_level', 75) * 2,
            'bwd_packets_length_total': traffic_data.get('traffic_level', 75) * 1.5,
            'fwd_packet_length_max': random.uniform(0.8, 2.5),
            'fwd_packet_length_min': random.uniform(0.1, 0.9),
            'flow_iat_mean': random.uniform(0.5, 2.0),
            'flow_iat_std': random.uniform(0.2, 1.0),
            'flow_iat_max': random.uniform(1.0, 3.0),
            'flow_iat_min': random.uniform(0.1, 0.5),
            'fwd_iat_mean': random.uniform(0.5, 2.0),
            'fwd_iat_std': random.uniform(0.2, 1.0),
            'fwd_iat_max': random.uniform(1.0, 3.0),
            'fwd_iat_min': random.uniform(0.1, 0.5),
            'bwd_iat_mean': random.uniform(0.5, 2.0),
            'bwd_iat_std': random.uniform(0.2, 1.0),
            'bwd_iat_max': random.uniform(1.0, 3.0),
            'bwd_iat_min': random.uniform(0.1, 0.5),
            'source_ip': traffic_data.get('source_ips', ['192.168.1.100'])[0]
        }
        
        # Try to make a real API call to the model endpoint
        try:
            response = requests.post(
                'http://localhost:5000/api/threat-detection',
                json=model_input,
                timeout=1
            )
            if response.status_code == 200:
                model_result = response.json()
            else:
                # Fall back to simulated result
                raise Exception(f"API returned status code {response.status_code}")
        except Exception:
            # Simulate model result
            attack_prob = traffic_data.get('attack_probability', 0.1)
            model_result = {
                'threat_score': attack_prob,
                'feature_importance': {
                    'flow_duration': random.uniform(0.1, 0.9),
                    'total_fwd_packets': random.uniform(0.1, 0.9),
                    'total_backward_packets': random.uniform(0.1, 0.9),
                    'fwd_packets_length_total': random.uniform(0.1, 0.9),
                    'bwd_packets_length_total': random.uniform(0.1, 0.9)
                },
                'defense_action': {
                    'action_type': 'block' if attack_prob > 0.6 else 'monitor',
                    'confidence': attack_prob,
                    'details': 'Automated defense action based on threat score'
                },
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'model_type': 'rl'
            }
        
        # Combine original data with model predictions
        return {
            **traffic_data,
            'model_prediction': model_result
        }
        
    except Exception as e:
        logger.error(f"Error integrating model predictions: {e}")
        return traffic_data