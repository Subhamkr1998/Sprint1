import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'expense_tracker')
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    
    # Ensure the upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Server configuration
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True

    # Application configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here') 