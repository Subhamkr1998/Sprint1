import os
import sys
import webbrowser
from threading import Timer
from app import app
from config import Config

def open_browser():
    """Open the browser to the application URL after a short delay"""
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == "__main__":
    # Check if Flask is installed
    try:
        from flask import Flask
    except ImportError:
        print("Flask is not installed. Installing Flask...")
        os.system(f"{sys.executable} -m pip install flask")
    
    # Set Flask environment variables
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'
    
    # Open browser after a short delay
    Timer(1.5, open_browser).start()
    
    # Start the Flask application
    print("Starting Expense Tracker application...")
    print(f"Access the application at: http://{Config.HOST}:{Config.PORT}/")
    print("Press CTRL+C to stop the server.")
    
    # Run the Flask application
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    ) 