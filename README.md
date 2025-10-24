# 🎁 Wishlist Tracker

A self-hosted web application for tracking wishlist items with automatic price checking and history tracking.

## Features

- 📝 Track items with type, name, URL, and images
- 💰 Monitor current prices and price history
- 📊 Visualize price trends with interactive charts
- 🔄 One-click and scheduled price checks (every 24 hours)
- 📤 Export data to CSV
- 💾 All data stored in a single SQLite database file

## Technology Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Charts:** Chart.js
- **Price Fetching:** BeautifulSoup4, Requests

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/YOUR-USERNAME/wishlist-tracker.git
cd wishlist-tracker
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash
# OR
.venv\Scripts\activate  # Windows CMD
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to: http://localhost:5000

## Usage

### Adding Items

1. Click "Add Item" button
2. Fill in item details (type, name, URL, price)
3. Upload an image or enable auto-fetch from URL
4. Click "Add to Wishlist"

### Checking Prices

- **Single Item:** Click "Check Price" on any item card
- **All Items:** Click "Check All Prices" in the header
- **Automatic:** Prices are checked every 24 hours automatically

### Viewing Price History

Click "History" on any item to see a chart of price changes over time.

### Exporting Data

Click "Export CSV" to download all wishlist data as a CSV file.

## Project Structure

wishlist-tracker/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── price_checker.py       # Price fetching logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Frontend template
├── static/               # Static files
├── uploads/              # Uploaded images
└── instance/
└── wishlist.db       # SQLite database (created on first run)

## Database

The SQLite database file is stored in `instance/wishlist.db`. This single file contains all your wishlist data and can be easily backed up or transferred.

## Notes

- Price checking works best with common e-commerce sites
- Some websites may block automated price fetching
- Images are stored locally in the `uploads/` folder
- Scheduled price checks run every 24 hours while the app is running

## License

This project is open source and available under the MIT License.

## Contributing

Contributions, issues, and feature requests are welcome!