# Expense Tracker

A web-based expense tracking application built with Flask and MySQL. Track your daily expenses, set monthly budgets, and generate detailed reports.

## Features

- Track daily expenses with categories and descriptions
- Set and monitor monthly income and budget
- Visualize spending patterns with interactive charts
- Download monthly expense reports in Excel format
- Search and filter expenses
- Uses Indian Rupee (₹) as the currency

## Prerequisites

- Python 3.7 or higher
- MySQL Server
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd expense-tracker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up MySQL:
   - Install MySQL Server if not already installed
   - Create a new database named 'expense_tracker'
   - Update the `.env` file with your MySQL credentials

5. Initialize the database:
```bash
python init_db.py
```

## Configuration

Create a `.env` file in the project root with the following variables:
```
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DB=expense_tracker
SECRET_KEY=your-secret-key-here
```

## Running the Application

1. Start the Flask development server:
```bash
python run.py
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## Features in Detail

### Expense Management
- Add new expenses with amount, category, description, and date
- Delete existing expenses
- View all expenses in a sortable table
- Search expenses by date, description, or category

### Budget Tracking
- Set monthly income and budget
- Monitor spending against budget
- Visual progress bar showing budget utilization
- Warning indicators for high spending

### Reports
- Download monthly expense reports in Excel format
- Reports include:
  - Detailed expense list
  - Monthly summary with income, budget, and savings
  - Category-wise spending breakdown

### Data Visualization
- Interactive pie chart showing spending by category
- Real-time updates of expense data
- Monthly summary cards with key metrics

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 