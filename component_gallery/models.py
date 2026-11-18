from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    
    # Stores the raw HTML/CSS string to be rendered in the gallery
    code_snippet = db.Column(db.Text, nullable=False) 
    
    author = db.Column(db.String(50), default='Admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)