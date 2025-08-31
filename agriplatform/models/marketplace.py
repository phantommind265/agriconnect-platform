from agriplatform import db
from datetime import datetime

class MarketItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    seller_name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
