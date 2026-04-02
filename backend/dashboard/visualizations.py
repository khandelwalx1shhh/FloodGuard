import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np

def create_traffic_graph(df):
    """Create main traffic graph with traffic and blocked requests"""
    fig = go.Figure()
    
    # Add area for normal traffic
    fig.add_trace(go.Scatter(
        x=df['timestamp'], 
        y=df['traffic'],
        mode='lines',
        name='Traffic',
        line=dict(color='rgba(52, 152, 219, 0.8)', width=2),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.2)'
    ))
    
    # Add area for blocked requests
    fig.add_trace(go.Scatter(
        x=df['timestamp'], 
        y=df['blocked_requests'],
        mode='lines',
        name='Blocked',
        line=dict(color='rgba(231, 76, 60, 0.8)', width=2),
        fill='tozeroy',
        fillcolor='rgba(231, 76, 60, 0.2)'
    ))
    
    # Add markers for attack points with probability > 0.7
    attack_df = df[df['attack_probability'] > 0.7]
    if len(attack_df) > 0:
        fig.add_trace(go.Scatter(
            x=attack_df['timestamp'],
            y=attack_df['traffic'],
            mode='markers',
            marker=dict(
                symbol='triangle-up',
                size=12,
                color='red',
                line=dict(width=2, color='darkred')
            ),
            name='Attack Points',
            hoverinfo='text',
            hovertext=[f"Attack: {t}<br>Prob: {p:.2f}" for t, p in 
                     zip(attack_df['attack_type'], attack_df['attack_probability'])]
        ))
    
    fig.update_layout(
        template='plotly_dark',
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_title="Time",
        yaxis_title="Request Count",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        hovermode='closest'
    )
    
    return fig

def create_threat_gauge(probability):
    """Create a semicircular gauge for threat level visualization"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=probability,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Threat Level", 'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "rgba(255,255,255,0.5)"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 0.4], 'color': "rgba(146, 208, 80, 0.8)"},
                {'range': [0.4, 0.7], 'color': "rgba(255, 192, 0, 0.8)"},
                {'range': [0.7, 0.9], 'color': "rgba(255, 0, 0, 0.8)"},
                {'range': [0.9, 1.0], 'color': "rgba(112, 48, 160, 0.8)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': probability
            }
        }
    ))
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "white"}
    )
    
    return fig

def create_geo_map(attack_sources):
    """Create a geographical map of attack sources"""
    fig = px.scatter_geo(
        attack_sources,
        lat='latitude',
        lon='longitude',
        color='intensity',
        size='volume',
        hover_name='country',
        projection='natural earth',
        color_continuous_scale=px.colors.sequential.Plasma
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        geo=dict(
            showland=True,
            landcolor='rgb(30, 30, 30)',
            showocean=True,
            oceancolor='rgb(20, 20, 40)',
            showcountries=True,
            countrycolor='rgb(60, 60, 60)',
            showframe=False
        )
    )
    
    return fig

def create_traffic_sparkline(df):
    """Create a small sparkline graph for traffic trends"""
    recent_df = df.tail(30)  # Just use the most recent points for the sparkline
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=recent_df['timestamp'],
        y=recent_df['traffic'],
        mode='lines',
        line=dict(color='rgba(52, 152, 219, 1)', width=2),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.2)'
    ))
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_top_sources_chart(attack_sources):
    """Create a horizontal bar chart for top attack sources"""
    top_sources = attack_sources.sort_values('volume', ascending=False).head(8)
    
    fig = go.Figure(go.Bar(
        x=top_sources['volume'],
        y=top_sources['country'],
        orientation='h',
        marker=dict(
            color=top_sources['volume'],
            colorscale='Viridis',
            colorbar=dict(title='Volume')
        )
    ))
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Request Volume",
        yaxis=dict(autorange="reversed"),
        font=dict(color='white')
    )
    
    return fig