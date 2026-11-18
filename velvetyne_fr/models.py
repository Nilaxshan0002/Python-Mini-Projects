from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Font(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    font_family_css = db.Column(db.String(100))
    price = db.Column(db.Float, default=50.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    font_id = db.Column(db.Integer, db.ForeignKey('font.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # Relationship to easily access font data (e.g., item.font.name)
    font = db.relationship('Font')