
m flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from utils import generate_token

# Define Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='custom_templates')
    
    # Load configuration from environment variables or use defaults
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = generate_token()  # Set a secret key for session management
    
    # Configure Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'login'  # Specify the view for login
    
    # Initialize extensions
    db.init_app(app)
    
    # Additional app setup goes here
    
    return app
