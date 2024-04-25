from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Define Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='custom_templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'  # Set a secret key for session management

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Additional app setup goes here

    return app
