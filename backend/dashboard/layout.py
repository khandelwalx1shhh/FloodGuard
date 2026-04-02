import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

def create_dashboard_layout():
    return html.Div([
        # Header with simplified design - no logo or title
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        # Minimal header - removed logo and title
                        html.H4("DDoS Protection System", className="text-muted mb-0")
                    ], className="d-flex align-items-center")
                ], width=7),
                dbc.Col([
                    html.Div([
                        html.H3(id='current-time', children="--"),
                        html.H5(id='server-status', children="Server Status: Online", className="text-success")
                    ], className="text-end")
                ], width=5)
            ], className="header-row mb-3"),
            
            # Alert Banner for Critical Events
            html.Div(id='alert-banner', className="mb-3"),
            
            # Main Status Cards
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("Current Threat Status", className="card-title"),
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.H2(id='threat-level', children="Loading..."),
                                    html.Div(id='attack-type-display', children=""),
                                    # Threat Gauge
                                    dcc.Graph(id='threat-gauge', config={'displayModeBar': False}, 
                                             style={'height': '150px'})
                                ], className="text-center")
                            ])
                        ], className="status-card")
                    ], className="h-100")
                ], width=4),
                
                dbc.Col([
                    html.Div([
                        html.H4("Traffic Statistics", className="card-title"),
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Div([
                                        html.H3("Current Traffic", className="stat-title"),
                                        html.H2(id='traffic-value', children="Loading...")
                                    ], className="mb-2"),
                                    # Traffic sparkline
                                    dcc.Graph(id='traffic-sparkline', config={'displayModeBar': False},
                                              style={'height': '80px'})
                                ], className="text-center")
                            ])
                        ], className="status-card")
                    ], className="h-100")
                ], width=4),
                
                dbc.Col([
                    html.Div([
                        html.H4("Protection Status", className="card-title"),
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Div([
                                        html.H3("Blocked Requests", className="stat-title"),
                                        html.H2(id='blocked-value', children="Loading...")
                                    ], className="mb-2"),
                                    # Blocked requests indicator
                                    dcc.Graph(id='block-rate-indicator', config={'displayModeBar': False},
                                             style={'height': '80px'})
                                ], className="text-center")
                            ])
                        ], className="status-card")
                    ], className="h-100")
                ], width=4),
            ], className="mb-4"),
            
            # Traffic Graph
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("Traffic Over Time", className="graph-title"),
                        html.Div([
                            dbc.ButtonGroup([
                                dbc.Button("1h", id="1h-button", className="time-button"),
                                dbc.Button("6h", id="6h-button", className="time-button"),
                                dbc.Button("24h", id="24h-button", className="time-button active"),
                            ], className="mb-2")
                        ], className="text-end"),
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(id='traffic-graph', config={'displayModeBar': False})
                            ])
                        ]),
                        # Increased the interval to 5 seconds (5000ms) to slow down updates
                        dcc.Interval(
                            id='interval-component',
                            interval=5*1000,  # in milliseconds (5 seconds)
                            n_intervals=0
                        )
                    ])
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Attack Probability Trend", className="graph-title"),
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='attack-prob-graph', config={'displayModeBar': False})
                        ])
                    ])
                ], width=6),
                
                dbc.Col([
                    html.H4("Attack Distribution", className="graph-title"),
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='attack-distribution', config={'displayModeBar': False})
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),
            
            # New visualization row
            dbc.Row([
                dbc.Col([
                    html.H4("Geographical Attack Source", className="graph-title"),
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='geo-map', config={'displayModeBar': False})
                        ])
                    ])
                ], width=8),
                
                dbc.Col([
                    html.H4("Top Attack Sources", className="graph-title"),
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='top-sources', config={'displayModeBar': False})
                        ])
                    ])
                ], width=4)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Real-time Logs", className="log-title d-flex justify-content-between"),
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id='log-container', className="logs-container")
                        ])
                    ])
                ], width=12)
            ])
            
        ], fluid=True, className="dashboard-container")
    ])