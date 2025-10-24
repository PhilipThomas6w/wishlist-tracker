from flask import Flask, render_template, request, jsonify, send_file
from models import db, WishlistItem, PriceHistory
from price_checker import PriceChecker
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import os
import csv
import io
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'wishlist.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db.init_app(app)
price_checker = PriceChecker()

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('instance', exist_ok=True)

# Initialize database
with app.app_context():
    db.create_all()

# Scheduler for automatic price checks
scheduler = BackgroundScheduler()
scheduler.start()

def check_all_prices():
    """Background task to check all prices"""
    with app.app_context():
        items = WishlistItem.query.filter(WishlistItem.url.isnot(None)).all()
        for item in items:
            price = price_checker.fetch_price(item.url)
            if price:
                item.current_price = price
                item.last_checked = datetime.utcnow()
                
                # Add to price history
                history = PriceHistory(item_id=item.id, price=price)
                db.session.add(history)
        
        db.session.commit()
        print(f"Price check completed at {datetime.utcnow()}")

# Schedule price checks every 24 hours
scheduler.add_job(func=check_all_prices, trigger="interval", hours=24, id='price_check')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/items', methods=['GET'])
def get_items():
    items = WishlistItem.query.all()
    return jsonify([item.to_dict() for item in items])

@app.route('/api/items', methods=['POST'])
def add_item():
    data = request.form
    
    # Create new item
    item = WishlistItem(
        item_type=data.get('item_type'),
        item_name=data.get('item_name'),
        url=data.get('url'),
        current_price=float(data.get('current_price')) if data.get('current_price') else None,
        currency=data.get('currency', 'GBP')
    )
    
    # Handle image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            item.image_path = filepath
    
    # Auto-fetch image from URL if no upload
    elif data.get('url') and data.get('auto_fetch_image') == 'true':
        image_url = price_checker.fetch_image_url(data.get('url'))
        if image_url:
            try:
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    filename = secure_filename(f"{datetime.now().timestamp()}_fetched.jpg")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    item.image_path = filepath
            except Exception as e:
                print(f"Error downloading image: {e}")
    
    db.session.add(item)
    db.session.flush()  # This assigns the ID to the item
    
    # Add initial price to history
    if item.current_price:
        history = PriceHistory(item_id=item.id, price=item.current_price)
        db.session.add(history)
    
    db.session.commit()
    
    return jsonify(item.to_dict()), 201

@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = WishlistItem.query.get_or_404(item_id)
    data = request.json
    
    if 'item_type' in data:
        item.item_type = data['item_type']
    if 'item_name' in data:
        item.item_name = data['item_name']
    if 'url' in data:
        item.url = data['url']
    if 'current_price' in data:
        new_price = float(data['current_price'])
        if new_price != item.current_price:
            item.current_price = new_price
            history = PriceHistory(item_id=item.id, price=new_price)
            db.session.add(history)
    
    db.session.commit()
    return jsonify(item.to_dict())

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = WishlistItem.query.get_or_404(item_id)
    
    # Delete image file if exists
    if item.image_path and os.path.exists(item.image_path):
        os.remove(item.image_path)
    
    db.session.delete(item)
    db.session.commit()
    
    return '', 204

@app.route('/api/items/<int:item_id>/check-price', methods=['POST'])
def check_price(item_id):
    item = WishlistItem.query.get_or_404(item_id)
    
    if not item.url:
        return jsonify({'error': 'No URL provided'}), 400
    
    price = price_checker.fetch_price(item.url)
    
    if price:
        item.current_price = price
        item.last_checked = datetime.utcnow()
        
        # Add to price history
        history = PriceHistory(item_id=item.id, price=price)
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'price': price,
            'last_checked': item.last_checked.isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Could not fetch price'
        }), 400

@app.route('/api/items/<int:item_id>/price-history', methods=['GET'])
def get_price_history(item_id):
    history = PriceHistory.query.filter_by(item_id=item_id).order_by(PriceHistory.checked_at).all()
    return jsonify([h.to_dict() for h in history])

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    items = WishlistItem.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Type', 'Name', 'URL', 'Current Price', 'Currency', 'Created At', 'Last Checked'])
    
    # Write data
    for item in items:
        writer.writerow([
            item.id,
            item.item_type,
            item.item_name,
            item.url or '',
            item.current_price or '',
            item.currency,
            item.created_at.isoformat() if item.created_at else '',
            item.last_checked.isoformat() if item.last_checked else ''
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'wishlist_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True, port=5000)