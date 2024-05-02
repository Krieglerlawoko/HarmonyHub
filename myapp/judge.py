from utils.database import db
from flask import Flask, current_app
from app import app

def some_function():
    db = current_app.db
    # rest of your code
    db = current_app.db
    # rest of your code
    db.drop_all()
    db.create_all()



some_function()
