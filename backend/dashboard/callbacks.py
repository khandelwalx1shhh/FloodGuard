from dash import Input, Output, State, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
import random
import logging
from datetime import datetime
from dashboard.visualizations import (
    create_traffic_graph,
    create_threat_gauge,
    create_traffic_sparkline,
    create_geo_map,
    create_top_sources_chart
)

logger = logging.getLogger(__name__)

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

def register_callbacks(app, socketio):
    """Register all Dash callbacks"""
    
    # Update metrics based on interval
    @app.callback(
        [
            Output('threat-level', 'children'),
            Output('threat-level', 'style'),
            Output('traffic-value', 'children'),
            Output('blocked-value', 'children'),
            Output('traffic-graph', 'figure'),
            Output('attack-prob-graph', 'figure'),
            Output('attack-distribution', 'figure'),
            Output('attack-type-display', 'children'),
            Output('log-container', 'children'),
            Output('threat-gauge', 'figure'),
            Output('traffic-sparkline', 'figure'),
            Output('geo-map', 'figure'),
            Output('top-sources', 'figure'),
            Output('current-time', 'children'),
            Output('alert-banner', 'children'),
            Output('block-rate-indicator', 'figure')
        ],
        [Input('interval-component', 'n_intervals')]
    )
    def update_metrics(n):
        try:
            # Get current time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Load the current data
            try:
                with open('latest_attack_data.json', 'r') as f:
                    latest = json.load(f)
            except Exception as e:
                logger.error(f"Error loading latest data: {e}")
                latest = {
                    'timestamp': current_time,
                    'traffic_level': 50,
                    'attack_probability': 0.1,
                    'attack_type': None,
                    'blocked_requests': 0,
                    'threat_level': 'Low'
                }
            
            # Load historical data or generate placeholder
            try:
                with open('historical_data.json', 'r') as f:
                    historical_data = json.load(f)
                    df = pd.DataFrame(historical_data)
                    # Convert timestamp strings to datetime
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
            except Exception as e:
                logger.error(f"Error loading historical data: {e}")
                # Generate placeholder data
                from datetime import timedelta
                
                hours = 24
                time_points = [datetime.now() - timedelta(hours=hours) + 
                               timedelta(minutes=i*5) for i in range(hours*12)]
                
                df = pd.DataFrame({
                    'timestamp': time_points,
                    'traffic': [50 + 20*np.sin(i/10) for i in range(hours*12)],
                    'attack_probability': [0.1 + 0.1*np.sin(i/8) for i in range(hours*12)],
                    'attack_type': ['Normal'] * (hours*12),
                    'blocked_requests': [5 + 2*np.sin(i/10) for i in range(hours*12)]
                })
            
            # Add the latest point to our dataset for graphs
            new_time = datetime.strptime(latest['timestamp'], '%Y-%m-%d %H:%M:%S') if isinstance(latest['timestamp'], str) else latest['timestamp']
            
            attack_type = latest.get('attack_type', 'Normal')
            if not attack_type:
                attack_type = 'Normal'
                
            new_row = pd.DataFrame({
                'timestamp': [new_time],
                'traffic': [latest['traffic_level']],
                'attack_probability': [latest['attack_probability']],
                'attack_type': [attack_type],
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
                    html.H4("Attack Type Detected:", className="mt-2"),
                    html.H3(latest['attack_type'], style={'color': 'red', 'fontWeight': 'bold'})
                ])
            
            # Create all visualizations
            traffic_fig = create_traffic_graph(viz_df)
            threat_gauge_fig = create_threat_gauge(latest['attack_probability'])
            traffic_sparkline_fig = create_traffic_sparkline(viz_df)
            
            # Create geo map data (placeholder)
            countries = ['United States', 'China', 'Russia', 'Brazil', 'India', 
                      'Germany', 'United Kingdom', 'France', 'Japan', 'Canada']
            
            attack_sources = pd.DataFrame({
                'country': countries,
                'latitude': [37.0902, 35.8617, 61.5240, -14.2350, 20.5937, 
                           51.1657, 55.3781, 46.2276, 36.2048, 56.1304],
                'longitude': [-95.7129, 104.1954, 105.3188, -51.9253, 78.9629, 
                            10.4515, -3.4360, 2.2137, 138.2529, -106.3468],
                'intensity': [random.random() for _ in range(10)],
                'volume': [random.randint(10, 1000) for _ in range(10)]
            })
            
            geo_map_fig = create_geo_map(attack_sources)
            top_sources_fig = create_top_sources_chart(attack_sources)
            
            # Attack probability graph
            prob_fig = go.Figure()
            prob_fig.add_trace(go.Scatter(
                x=viz_df['timestamp'], 
                y=viz_df['attack_probability'],
                mode='lines',
                name='Attack Probability',
                line=dict(color='#e74c3c', width=2),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.2)'
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
                yaxis_title="Probability",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff')
            )
            
            # For the attack distribution graph, add smoother transitions with frames
            attack_counts = viz_df[viz_df['attack_type'] != 'Normal']['attack_type'].value_counts().reset_index()
            attack_counts.columns = ['attack_type', 'count']
            
            # Color mapping for attack types
            ATTACK_TYPES = {
                'SYN Flood': {'color': '#FF5733'},
                'HTTP Flood': {'color': '#33A8FF'},
                'UDP Flood': {'color': '#FF33A8'},
                'Slowloris': {'color': '#A833FF'},
                'DNS Amplification': {'color': '#33FFA8'}
            }
            
            if len(attack_counts) > 0:
                # Use a bar chart with animation configuration
                attack_dist_fig = px.bar(
                    attack_counts, 
                    x='attack_type', 
                    y='count',
                    color='attack_type',
                    color_discrete_map={t: ATTACK_TYPES.get(t, {}).get('color', '#777') for t in attack_counts['attack_type']},
                    template='plotly_dark'
                )
                
                attack_dist_fig.update_layout(
                    transition_duration=500,  # Enable smooth transition
                    margin=dict(l=20, r=20, t=30, b=40),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff'),
                    xaxis_title="Attack Type",
                    yaxis_title="Count"
                )
            else:
                # Create an empty chart with a message
                attack_dist_fig = go.Figure()
                attack_dist_fig.add_annotation(
                    text="No attacks detected in timeframe",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16, color="#9e9e9e")
                )
                attack_dist_fig.update_layout(
                    template='plotly_dark',
                    margin=dict(l=20, r=20, t=30, b=20),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff')
                )
            
            # For all graphs, add transition configuration
            traffic_fig.update_layout(transition_duration=500)
            prob_fig.update_layout(transition_duration=500)
            geo_map_fig.update_layout(transition_duration=500)
            top_sources_fig.update_layout(transition_duration=500)
            
            # Create a simple block rate indicator
            block_rate = latest['blocked_requests'] / max(1, latest['traffic_level'])
            block_indicator_fig = go.Figure()
            block_indicator_fig.add_trace(go.Indicator(
                mode="gauge",
                value=block_rate * 100,  # Convert to percentage
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 0, 'visible': False},
                    'bar': {'color': "rgba(231, 76, 60, 0.7)"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 0,
                }
            ))
            block_indicator_fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': "white"},
                transition_duration=500  # Smooth transition
            )

            # Create recent logs with fade-in animation
            recent_logs = [
                html.Div(f"[{latest['timestamp']}] {'🚨 ' if latest['attack_type'] else ''}Traffic: {latest['traffic_level']:.0f} req/s, Blocked: {latest['blocked_requests']}", 
                        className="log-entry"),
                html.Div(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] System status: monitoring", 
                        className="log-entry"),
                html.Div(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'Attack detected: ' + latest['attack_type'] if latest['attack_type'] else 'No active threats'}", 
                        className="log-entry"),
                html.Div(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Threat level: {latest['threat_level']}", 
                        className="log-entry")
            ]
            
            # Create alert banner only if under attack
            alert_banner = ""
            if latest['attack_probability'] > 0.7 and latest['attack_type']:
                alert_banner = dbc.Alert([
                    html.H4(f"⚠️ Active {latest['attack_type']} Attack Detected", className="alert-heading mb-0"),
                    html.Div(f"Threat Level: {latest['threat_level']} | Blocked: {latest['blocked_requests']} requests")
                ], color="danger", className="mb-3")
            
            return (
                threat_level,
                {'color': threat_color, 'transition': 'all 0.5s ease'},  # Add transition to the style
                f"{latest['traffic_level']:.0f} req/s",
                f"{latest['blocked_requests']} ({block_rate*100:.1f}%)",
                traffic_fig,
                prob_fig,
                attack_dist_fig,
                attack_display,
                recent_logs,
                threat_gauge_fig,
                traffic_sparkline_fig, 
                geo_map_fig,
                top_sources_fig,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                alert_banner,
                block_indicator_fig
            )
        
        except Exception as e:
            logger.error(f"Error in update_metrics: {e}")
            # Return default values if there's an error
            return (
                "Error",
                {'color': 'red'},
                "N/A",
                "N/A",
                go.Figure(),
                go.Figure(),
                go.Figure(),
                "",
                [html.Div("Error loading data")],
                go.Figure(),
                go.Figure(),
                go.Figure(),
                go.Figure(),
                "Error loading time",
                html.Div(),
                go.Figure()
            )