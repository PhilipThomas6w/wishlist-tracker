import os
import sys
import webbrowser
import time
from threading import Timer
import socket

def is_port_in_use(port):
    """Check if port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def open_browser():
    """Open browser after a short delay"""
    webbrowser.open('http://localhost:5000')
    print("\n✓ Browser opened at http://localhost:5000")
    print("✓ Wishlist Tracker is running")
    print("\nPress CTRL+C to stop the server\n")

if __name__ == '__main__':
    # Check if already running
    if is_port_in_use(5000):
        print("⚠ Wishlist Tracker is already running!")
        print("Opening browser...")
        webbrowser.open('http://localhost:5000')
        input("\nPress Enter to exit...")
        sys.exit(0)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 50)
    print("🎁 Starting Wishlist Tracker...")
    print("=" * 50)
    
    # Open browser after 2 seconds
    Timer(2, open_browser).start()
    
    # Import and run the Flask app
    from app import app
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n✓ Wishlist Tracker stopped")
        print("=" * 50)