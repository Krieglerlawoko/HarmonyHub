from flask import render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(16)
pp.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


db = SQLAlchemy(app)
uploads = UploadSet('uploads', IMAGES)
configure_uploads(app, uploads)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Import and register routes after initializing db to avoid circular import issues
from routes import *

if __name__ == '__main__':
    app.run(debug=True)
