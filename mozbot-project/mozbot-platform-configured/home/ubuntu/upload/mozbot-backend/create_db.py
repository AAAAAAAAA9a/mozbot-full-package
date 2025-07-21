import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models import db

with app.app_context():
    db.create_all()
    print("Database tables created successfully")


