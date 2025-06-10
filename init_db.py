import mysql.connector
from config import Config

def init_database():
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            auth_plugin='mysql_native_password'
        )
        cursor = conn.cursor()

        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
        cursor.execute(f"USE {Config.MYSQL_DB}")

        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS expenses")
        cursor.execute("DROP TABLE IF EXISTS settings")

        # Create expenses table
        cursor.execute('''
            CREATE TABLE expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                amount DECIMAL(10,2) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description TEXT,
                date DATE NOT NULL
            )
        ''')

        # Create settings table
        cursor.execute('''
            CREATE TABLE settings (
                setting_key VARCHAR(50),
                value TEXT NOT NULL,
                user_id VARCHAR(50),
                PRIMARY KEY (setting_key, user_id)
            )
        ''')

        # Insert default settings
        cursor.execute('''
            INSERT INTO settings (setting_key, value, user_id)
            VALUES 
                ('monthly_income', '0', 'default'),
                ('monthly_expense', '0', 'default')
        ''')

        conn.commit()
        print("Database initialized successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    init_database() 