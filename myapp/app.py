from flask import render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from utils import generate_token

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = generate_token() 


db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Import and register routes after initializing db to avoid circular import issues
from routes import *

if __name__ == '__main__':
    app.run(debug=True)
