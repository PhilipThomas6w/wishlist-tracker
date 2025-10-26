import sqlite3
import os
from app import app
from models import db, WishlistItem

def migrate():
    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'wishlist.db')
    
    # Connect directly with sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(wishlist_items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'order_index' not in columns:
            print("Adding order_index column...")
            cursor.execute("ALTER TABLE wishlist_items ADD COLUMN order_index INTEGER DEFAULT 0")
            conn.commit()
            print("Column added successfully!")
        else:
            print("Column already exists.")
        
        # Now set order indices using Flask app context
        with app.app_context():
            items = WishlistItem.query.order_by(WishlistItem.created_at).all()
            
            print(f"Setting order indices for {len(items)} items...")
            for index, item in enumerate(items):
                item.order_index = index
            
            db.session.commit()
            print(f"Successfully updated {len(items)} items with order indices")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()