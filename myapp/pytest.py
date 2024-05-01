from app import db
from models import *

user = User.query.filter_by(username=username).first()
