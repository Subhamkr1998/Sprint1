from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, session
import mysql.connector
from datetime import datetime, date
import pandas as pd
import os
from config import Config
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

# Secret key for session management
app.secret_key = 'your_secret_key_here'

# Ensure the reports directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            auth_plugin='mysql_native_password',
            connect_timeout=10
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        if err.errno == 1045:  # Access denied error
            print("Please check your MySQL username and password in the .env file")
        elif err.errno == 1049:  # Database does not exist
            print("Please run init_db.py first to create the database")
        raise

def generate_pdf_report(expenses_df, settings_df):
    # Create PDF file path
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'monthly_report.pdf')
    
    # Create the PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    elements.append(Paragraph("Monthly Expense Report", title_style))
    
    # Add date
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20
    )
    elements.append(Paragraph(f"Generated on: {date.today().strftime('%B %d, %Y')}", date_style))
    
    # Add summary section
    elements.append(Paragraph("Summary", styles['Heading2']))
    summary_data = [
        ['Metric', 'Amount (₹)'],
        ['Monthly Income', f"₹{settings_df['monthly_income'].iloc[0]:,.2f}"],
        ['Monthly Budget', f"₹{settings_df['monthly_expense'].iloc[0]:,.2f}"],
        ['Total Expenses', f"₹{expenses_df['amount'].sum():,.2f}"],
        ['Net Savings', f"₹{settings_df['monthly_income'].iloc[0] - expenses_df['amount'].sum():,.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Add expenses section
    elements.append(Paragraph("Detailed Expenses", styles['Heading2']))
    expenses_data = [['Date', 'Category', 'Description', 'Amount (₹)']]
    for _, row in expenses_df.iterrows():
        expenses_data.append([
            row['date'].strftime('%Y-%m-%d'),
            row['category'],
            row['description'],
            f"₹{row['amount']:,.2f}"
        ])
    
    expenses_table = Table(expenses_data, colWidths=[1*inch, 1.5*inch, 2.5*inch, 1.5*inch])
    expenses_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(expenses_table)
    
    # Build the PDF
    doc.build(elements)
    return pdf_path

# User data storage (for simplicity, using a dictionary; replace with a database in production)
users = {}

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return 'User already exists!'
        users[username] = generate_password_hash(password)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_password_hash = users.get(username)
        if user_password_hash and check_password_hash(user_password_hash, password):
            session['user'] = username
            return redirect(url_for('index'))
        return 'Invalid credentials!'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current month's expenses
        current_month = datetime.now().strftime('%Y-%m')
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM expenses 
            WHERE DATE_FORMAT(date, '%Y-%m') = %s
        ''', (current_month,))
        monthly_expenses = float(cursor.fetchone()['total'])
        
        # Get monthly income and expense from settings
        cursor.execute('SELECT setting_key, value FROM settings WHERE setting_key IN ("monthly_income", "monthly_expense")')
        settings = {row['setting_key']: float(row['value']) for row in cursor.fetchall()}
        
        monthly_income = settings.get('monthly_income', 0.0)
        monthly_expense_limit = settings.get('monthly_expense', 0.0)
        
        # Calculate savings
        savings = monthly_income - monthly_expenses if monthly_income > 0 else 0
        
        # Calculate budget warning
        budget_warning = {
            'percentage': (monthly_expenses / monthly_expense_limit * 100) if monthly_expense_limit > 0 else 0,
            'is_exceeded': monthly_expenses > monthly_expense_limit if monthly_expense_limit > 0 else False,
            'remaining': monthly_expense_limit - monthly_expenses if monthly_expense_limit > 0 else 0
        }
        
        # Get current month's expenses by category
        cursor.execute('''
            SELECT category, COALESCE(SUM(amount), 0) as total 
            FROM expenses 
            WHERE DATE_FORMAT(date, '%Y-%m') = %s
            GROUP BY category
        ''', (current_month,))
        category_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('index.html', 
                             monthly_expenses=monthly_expenses,
                             monthly_income=monthly_income,
                             monthly_budget=monthly_expense_limit,
                             savings=savings,
                             category_data=category_data,
                             budget_warning=budget_warning,
                             user=session['user'])
    except Exception as e:
        print(f"Error in index route: {str(e)}")
        return render_template('index.html', 
                             monthly_expenses=0,
                             monthly_income=0,
                             monthly_budget=0,
                             savings=0,
                             category_data=[],
                             budget_warning={'percentage': 0, 'is_exceeded': False, 'remaining': 0},
                             user=session['user'])

@app.route('/add_expense', methods=['POST'])
def add_expense():
    try:
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        date_str = request.form['date']
        expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        print(f"Adding expense: amount={amount}, category={category}, description={description}, date={expense_date}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO expenses (amount, category, description, date)
            VALUES (%s, %s, %s, %s)
        """, (amount, category, description, expense_date))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error adding expense: {e}")
        return redirect(url_for('index'))

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error deleting expense: {e}")
        return redirect(url_for('index'))

@app.route('/update_income', methods=['POST'])
def update_income():
    try:
        if 'income' not in request.form:
            return jsonify({'success': False, 'error': 'Income value is required'}), 400
            
        income = float(request.form['income'])
        if income < 0:
            return jsonify({'success': False, 'error': 'Income cannot be negative'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = session.get('user', 'default')

        # First try to update, if no rows affected then insert
        cursor.execute('''
            UPDATE settings 
            SET value = %s 
            WHERE setting_key = 'monthly_income' AND user_id = %s
        ''', (str(income), user_id))
        
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO settings (setting_key, value, user_id) 
                VALUES ('monthly_income', %s, %s)
            ''', (str(income), user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid income value'}), 400
    except mysql.connector.Error as err:
        print(f"Database error updating income: {err}")
        return jsonify({'success': False, 'error': f'Database error: {str(err)}'}), 500
    except Exception as e:
        print(f"Error updating income: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/update_budget', methods=['POST'])
def update_budget():
    try:
        if 'budget' not in request.form:
            return jsonify({'success': False, 'error': 'Budget value is required'}), 400
            
        budget = float(request.form['budget'])
        if budget < 0:
            return jsonify({'success': False, 'error': 'Budget cannot be negative'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = session.get('user', 'default')

        # First try to update, if no rows affected then insert
        cursor.execute('''
            UPDATE settings 
            SET value = %s 
            WHERE setting_key = 'monthly_expense' AND user_id = %s
        ''', (str(budget), user_id))
        
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO settings (setting_key, value, user_id) 
                VALUES ('monthly_expense', %s, %s)
            ''', (str(budget), user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid budget value'}), 400
    except mysql.connector.Error as err:
        print(f"Database error updating budget: {err}")
        return jsonify({'success': False, 'error': f'Database error: {str(err)}'}), 500
    except Exception as e:
        print(f"Error updating budget: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/expenses')
def get_expenses():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        expenses = cursor.fetchall()
        print("Fetched expenses:", expenses)
        
        cursor.close()
        conn.close()
        
        return jsonify(expenses)
    except Exception as e:
        print(f"Error getting expenses: {e}")
        return jsonify([])

@app.route('/api/categories')
def get_categories():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current month's expenses by category
        current_month = datetime.now().strftime('%Y-%m')
        cursor.execute('''
            SELECT category as name, COALESCE(SUM(amount), 0) as value
            FROM expenses
            WHERE DATE_FORMAT(date, "%Y-%m") = %s
            GROUP BY category
            HAVING value > 0
        ''', (current_month,))
        categories = cursor.fetchall()
        print("Fetched categories:", categories)
        
        return jsonify(categories)
    except Exception as e:
        print(f"Error getting categories: {str(e)}")
        return jsonify([])
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/monthly_summary')
def get_monthly_summary():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current month's expenses
        current_month = datetime.now().strftime('%Y-%m')
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE DATE_FORMAT(date, "%Y-%m") = %s
        ''', (current_month,))
        monthly_expenses = float(cursor.fetchone()['total'])
        
        # Get monthly income from settings
        cursor.execute('SELECT value FROM settings WHERE setting_key = "monthly_income"')
        result = cursor.fetchone()
        monthly_income = float(result['value']) if result else 0
        
        # Calculate savings (only if there are expenses in the current month)
        savings = monthly_income - monthly_expenses if monthly_expenses > 0 else monthly_income
        
        print("Monthly summary data:", {
            'monthly_expenses': monthly_expenses,
            'monthly_income': monthly_income,
            'savings': savings
        })
        
        return jsonify({
            'monthly_expenses': monthly_expenses,
            'monthly_income': monthly_income,
            'savings': savings
        })
    except Exception as e:
        print(f"Error in monthly summary: {str(e)}")
        return jsonify({
            'monthly_expenses': 0,
            'monthly_income': 0,
            'savings': 0
        })
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

@app.route('/download_report')
def download_report():
    try:
        conn = get_db_connection()
        
        # Get current month's data
        current_month = date.today().replace(day=1)
        
        # Get expenses
        expenses_df = pd.read_sql("""
            SELECT date, category, description, amount
            FROM expenses
            WHERE date >= %s
            ORDER BY date
        """, conn, params=(current_month,))
        
        # Get settings
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT setting_key, value FROM settings WHERE setting_key IN ("monthly_income", "monthly_expense")')
        settings = {row['setting_key']: float(row['value']) for row in cursor.fetchall()}
        
        # Create settings DataFrame
        settings_df = pd.DataFrame({
            'monthly_income': [settings.get('monthly_income', 0.0)],
            'monthly_expense': [settings.get('monthly_expense', 0.0)]
        })
        
        # Generate PDF report
        pdf_path = generate_pdf_report(expenses_df, settings_df)
        
        # Generate Excel report
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'monthly_report.xlsx')
        with pd.ExcelWriter(excel_path) as writer:
            # Write expenses sheet
            expenses_df.to_excel(writer, sheet_name='Expenses', index=False)
            
            # Write summary sheet
            summary_data = {
                'Metric': ['Monthly Income', 'Monthly Budget', 'Total Expenses', 'Net Savings'],
                'Amount': [
                    settings_df['monthly_income'].iloc[0],
                    settings_df['monthly_expense'].iloc[0],
                    expenses_df['amount'].sum(),
                    settings_df['monthly_income'].iloc[0] - expenses_df['amount'].sum()
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        cursor.close()
        conn.close()
        
        # Return PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'monthly_report_{date.today().strftime("%Y_%m")}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Error generating report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)