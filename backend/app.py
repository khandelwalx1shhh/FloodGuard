from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_socketio import SocketIO
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import os
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from dotenv import load_dotenv

# Import local modules
from dashboard.layout import create_dashboard_layout
from simulation.data_generator import simulate_ddos
from data_provider_v3 import get_latest_attack_data, get_attack_statistics, get_historical_attack_data, get_network_data, integrate_model_predictions

# Import callbacks independently to ensure proper loading
from dashboard.callbacks import register_callbacks

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Ensure assets folder exists
os.makedirs('assets', exist_ok=True)

# Initialize Flask - use the templates and static folders from the backend directory
server = Flask(__name__,
            static_url_path='/static',
            static_folder='static',
            template_folder='templates')
server.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
socketio = SocketIO(server, cors_allowed_origins="*")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = 'login'

# Mock User Database (replace with real database in production)
users = {}

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Create admin user
admin_user = User('1', 'admin', generate_password_hash('admin'))
users['1'] = admin_user

# Routes
@server.route('/')
def index():
    return render_template('index.html')

@server.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if username and password match the admin credentials
        if username == 'admin' and check_password_hash(users['1'].password_hash, password):
            # Log in the admin user
            login_user(users['1'])
            logger.info(f"User {username} logged in successfully")
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            flash('Invalid username or password', 'danger')
    
    # Show the login page for GET requests or failed login attempts
    return render_template('login.html')

@server.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if username and password and password == confirm_password:
            # In a real app, you'd check if the username already exists
            user_id = str(len(users) + 1)
            new_user = User(user_id, username, generate_password_hash(password))
            users[user_id] = new_user
            logger.info(f"New user registered: {username}")
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Please check your inputs.', 'danger')
    
    return render_template('register.html')

@server.route('/logout')
@login_required
def logout():
    logger.info(f"User {current_user.username} logged out")
    logout_user()
    return redirect(url_for('index'))

@server.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@server.route('/documentation')
def documentation():
    return render_template('documentation.html')

@server.route('/about')
def about():
    return render_template('about.html')

@server.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

# Email configuration
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'PUT YOUR EMAIL HERE')
# Use an app password for Gmail or other email providers
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'PUT YOUR APP PASSWORD HERE')

def send_notification(subject, body, recipient=None):
    """
    Send email notification
    """
    sender_email = EMAIL_ADDRESS
    receiver_email = recipient if recipient else EMAIL_ADDRESS
    password = EMAIL_PASSWORD

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        logger.info(f"Email notification sent to {receiver_email}")
        return {
            'success': True, 
            'message': 'Email notification sent successfully!'
        }
    except Exception as e:
        logger.error(f"Email error: {e}")
        return {'success': False, 'message': f'Error: {e}'}

@server.route('/send-alert', methods=['POST'])
@login_required
def send_alert():
    """
    API endpoint to send alert notifications via email
    """
    try:
        data = request.get_json()
        alert_type = data.get('alert_type', 'DDoS Alert')
        message = data.get('message', 'Potential DDoS attack detected!')
        recipient = data.get('recipient')
        
        # Add more details to the email body
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        email_subject = f"dDOS.Ai {alert_type}"
        email_body = f"""
DDoS Alert Notification
-----------------------
Time: {current_time}
Alert Type: {alert_type}
Message: {message}

This is an automated notification from your dDOS.Ai protection system.
Please check your dashboard for more details.

--
dDOS.Ai Security Team
"""
        
        result = send_notification(email_subject, email_body, recipient)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing alert request: {e}")
        return jsonify({'success': False, 'message': f'Error processing request: {str(e)}'})

# API endpoint to get attack data
@server.route('/api/attack-data', methods=['GET'])
@login_required
def get_attack_data():
    try:
        # Get basic data
        latest_data = get_latest_attack_data()
        
        # Get additional statistics if requested
        if request.args.get('stats') == 'true':
            stats_data = get_attack_statistics()
            return jsonify({'success': True, 'data': latest_data, 'statistics': stats_data})
        
        return jsonify({'success': True, 'data': latest_data})
    except Exception as e:
        logger.error(f"Error fetching attack data: {e}")
        return jsonify({'success': False, 'message': f'Error fetching data: {str(e)}'})

@server.route('/api/network-data', methods=['GET'])
@login_required
def get_network_visualization():
    try:
        data = get_network_data()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"Error fetching network visualization data: {e}")
        return jsonify({'success': False, 'message': f'Error fetching network data: {str(e)}'})

@server.route('/api/historical-data', methods=['GET'])
@login_required
def get_historical_data():
    try:
        # Parse hours parameter, default to 24
        hours = int(request.args.get('hours', 24))
        df = get_historical_attack_data(hours=hours)
        
        # Convert DataFrame to list of dictionaries for JSON serialization
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
            
        return jsonify({'success': True, 'data': records})
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        return jsonify({'success': False, 'message': f'Error fetching historical data: {str(e)}'})

@server.route('/api/model-prediction', methods=['POST'])
@login_required
def get_model_prediction():
    try:
        # Get traffic data from request
        data = request.get_json()
        if not data:
            data = get_latest_attack_data()
            
        # Get prediction
        prediction = integrate_model_predictions(data)
        return jsonify({'success': True, 'data': prediction})
    except Exception as e:
        logger.error(f"Error getting model prediction: {e}")
        return jsonify({'success': False, 'message': f'Error with model prediction: {str(e)}'})

# Create a healthcheck endpoint
@server.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': 'v3',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'endpoints': [
            '/api/attack-data',
            '/api/network-data',
            '/api/historical-data',
            '/api/model-prediction',
            '/dash/',
            '/dashboard'
        ]
    })

# Initialize Dash app
app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/dash/',
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    suppress_callback_exceptions=True
)
app.title = "DDoS.Ai Defense Monitor"

# Set the layout
app.layout = create_dashboard_layout()

# Register callbacks - This is the critical part that needs to be fixed
register_callbacks(app, socketio)

# Start the simulation thread
simulation_thread = threading.Thread(target=simulate_ddos, args=(socketio,), daemon=True)
simulation_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting dDOS.Ai V3 application on port {port}")
    socketio.run(server, debug=False, host='0.0.0.0', port=port)