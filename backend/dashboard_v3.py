import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import random
import json
from flask_socketio import emit
import logging

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

# Initial data
def generate_initial_data(hours=24):
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

# Helper functions for the dashboard
def get_threat_level(probability):
    for level, (min_val, max_val, _) in THREAT_LEVELS.items():
        if min_val <= probability < max_val:
            return level
    return 'Critical'

def get_threat_color(probability):
    for _, (min_val, max_val, color) in THREAT_LEVELS.items():
        if min_val <= probability < max_val:
            return color
    return THREAT_LEVELS['Critical'][2]

def simulate_ddos(socketio):
    """
    Continuously simulate DDoS attack data and emit updates via WebSockets.
    """
    logger.info("Starting DDoS simulation thread")
    df = generate_initial_data(hours=24)
    
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
            
            # Sleep for a while (1 second in simulation = 5 minutes in our data)
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error in simulation thread: {e}")
            time.sleep(5)  # Wait and try again

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

def create_dashboard(app):
    """
    Create the Dash dashboard layout and callbacks.
    """
    # Initial data
    df = generate_initial_data(hours=24)
    
    # Save initial data for API access
    latest_data = {
        'timestamp': df['timestamp'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S'),
        'traffic_level': df['traffic'].iloc[-1],
        'attack_probability': df['attack_probability'].iloc[-1],
        'attack_type': df['attack_type'].iloc[-1] if df['attack_type'].iloc[-1] != 'Normal' else None,
        'blocked_requests': df['blocked_requests'].iloc[-1],
        'threat_level': get_threat_level(df['attack_probability'].iloc[-1])
    }
    
    with open('latest_attack_data.json', 'w') as f:
        json.dump(latest_data, f, default=json_serialize_fix)
    
    # Dashboard layout
    app.layout = html.Div([
        dbc.Container([
          
            
            dbc.Row([
                dbc.Col([
                    html.H4("Current Threat Status"),
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.H2(id='threat-level', children="Loading..."),
                                html.Div(id='attack-type-display', children="")
                            ], style={'textAlign': 'center'})
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    html.H4("Traffic Statistics"),
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.H3("Current Traffic"),
                                html.H2(id='traffic-value', children="Loading...")
                            ], style={'textAlign': 'center'})
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    html.H4("Protection Status"),
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.H3("Blocked Requests"),
                                html.H2(id='blocked-value', children="Loading...")
                            ], style={'textAlign': 'center'})
                        ])
                    ])
                ], width=4),
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Traffic Over Time"),
                    dcc.Graph(id='traffic-graph'),
                    dcc.Interval(
                        id='interval-component',
                        interval=1*1000,  # in milliseconds
                        n_intervals=0
                    )
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Attack Probability"),
                    dcc.Graph(id='attack-prob-graph')
                ], width=6),
                
                dbc.Col([
                    html.H4("Attack Distribution"),
                    dcc.Graph(id='attack-distribution')
                ], width=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Real-time Logs"),
                    html.Div(id='log-container', style={
                        'maxHeight': '200px',
                        'overflow': 'auto',
                        'backgroundColor': '#1E1E1E',
                        'color': '#CCCCCC',
                        'padding': '10px',
                        'fontFamily': 'monospace'
                    })
                ], width=12)
            ])
            
        ], fluid=True)
    ])
    
    @app.callback(
        [Output('threat-level', 'children'),
         Output('threat-level', 'style'),
         Output('traffic-value', 'children'),
         Output('blocked-value', 'children'),
         Output('traffic-graph', 'figure'),
         Output('attack-prob-graph', 'figure'),
         Output('attack-distribution', 'figure'),
         Output('attack-type-display', 'children'),
         Output('log-container', 'children')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_metrics(n):
        try:
            # Load the current data (that would be updated by the simulation thread)
            with open('latest_attack_data.json', 'r') as f:
                latest = json.load(f)
            
            # Load historical data (from simulation thread)
            df = generate_initial_data(hours=24)
            
            # Add the latest point to our dataset for graphs
            new_time = datetime.strptime(latest['timestamp'], '%Y-%m-%d %H:%M:%S')
            new_row = pd.DataFrame({
                'timestamp': [new_time],
                'traffic': [latest['traffic_level']],
                'attack_probability': [latest['attack_probability']],
                'attack_type': [latest['attack_type'] if latest['attack_type'] else 'Normal'],
                'blocked_requests': [latest['blocked_requests']]
            })
            
            # Combine for visualization
            viz_df = pd.concat([df.iloc[-(min(288, len(df)-1)):], new_row], ignore_index=True)
            
            # Current threat level
            threat_level = latest['threat_level']
            threat_color = get_threat_color(latest['attack_probability'])
            
            # Display attack type if under attack
            attack_display = ""
            if latest['attack_type']:
                attack_display = html.Div([
                    html.H4("Attack Type Detected:"),
                    html.H3(latest['attack_type'], style={'color': 'red'})
                ])
            
            # Traffic graph
            traffic_fig = go.Figure()
            traffic_fig.add_trace(go.Scatter(
                x=viz_df['timestamp'], 
                y=viz_df['traffic'],
                mode='lines',
                name='Traffic',
                line=dict(color='#3498db', width=2)
            ))
            
            traffic_fig.add_trace(go.Scatter(
                x=viz_df['timestamp'], 
                y=viz_df['blocked_requests'],
                mode='lines',
                name='Blocked',
                line=dict(color='#e74c3c', width=2)
            ))
            
            traffic_fig.update_layout(
                template='plotly_dark',
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis_title="Time",
                yaxis_title="Request Count"
            )
            
            # Attack probability graph
            prob_fig = go.Figure()
            prob_fig.add_trace(go.Scatter(
                x=viz_df['timestamp'], 
                y=viz_df['attack_probability'],
                mode='lines',
                name='Attack Probability',
                line=dict(color='#e74c3c', width=2)
            ))
            
            prob_fig.update_layout(
                template='plotly_dark',
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis_title="Time",
                yaxis_title="Probability"
            )
            
            # Attack distribution graph
            attack_dist_fig = px.histogram(
                viz_df[viz_df['attack_type'] != 'Normal'],
                x='attack_type',
                color='attack_type',
                color_discrete_map={t: ATTACK_TYPES[t]['color'] for t in ATTACK_TYPES},
                template='plotly_dark'
            )
            
            attack_dist_fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis_title="Attack Type",
                yaxis_title="Count"
            )
            
            # Real-time logs
            logs = [
                f"{row['timestamp']} - Traffic: {row['traffic']}, Attack Probability: {row['attack_probability']:.2f}, Blocked: {row['blocked_requests']}"
                for _, row in viz_df.iterrows()
            ]
            
            return (
                threat_level,
                {'color': threat_color},
                f"{latest['traffic_level']:.2f} req/s",
                f"{latest['blocked_requests']}",
                traffic_fig,
                prob_fig,
                attack_dist_fig,
                attack_display,
                [html.Div(log) for log in logs]
            )
        
        except Exception as e:
            logger.error(f"Error in update_metrics: {e}")
            return (
                "Error",
                {'color': 'red'},
                "N/A",
                "N/A",
                go.Figure(),
                go.Figure(),
                go.Figure(),
                "",
                [html.Div("Error loading data")]
            )

if __name__ == '__main__':
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    create_dashboard(app)
    app.run_server(debug=True, port=8050)