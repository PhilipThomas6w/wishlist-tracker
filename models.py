from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class WishlistItem(db.Model):
    __tablename__ = 'wishlist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_type = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500))
    image_path = db.Column(db.String(500))
    current_price = db.Column(db.Float)
    currency = db.Column(db.String(10), default='USD')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_checked = db.Column(db.DateTime)
    
    # Relationship
    price_history = db.relationship('PriceHistory', backref='item', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_type': self.item_type,
            'item_name': self.item_name,
            'url': self.url,
            'image_path': self.image_path,
            'current_price': self.current_price,
            'currency': self.currency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None
        }

class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('wishlist_items.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'price': self.price,
            'checked_at': self.checked_at.isoformat()
        }