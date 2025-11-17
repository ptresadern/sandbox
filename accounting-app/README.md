# Personal Accounting App

A standalone desktop accounting application built with Python and tkinter for tracking personal income and expenses.

## Features

- **Transaction Management**: Add, view, and delete income and expense transactions
- **Receipt Scanning** (NEW): Upload receipt images to automatically extract transaction details
- **SQLite Database**: All data is stored locally in a SQLite database
- **Category-based Tracking**: Organize transactions by predefined or custom categories
- **Dashboard**: View summary statistics including total income, expenses, and net balance
- **Financial Reports**: Generate detailed summary and transaction reports
- **Export Functionality**: Export reports to text files for record-keeping
- **User-friendly GUI**: Simple and intuitive tkinter-based interface

## Requirements

- Python 3.6 or higher
- Built-in Python libraries:
  - tkinter (usually included with Python)
  - sqlite3 (included with Python)
  - datetime (included with Python)
- External packages (for receipt scanning feature):
  - Pillow: `pip install Pillow`
  - pytesseract: `pip install pytesseract`
  - Tesseract OCR engine (system dependency - see installation below)

## Installation

### Basic Installation

1. Clone or download this repository
2. Ensure Python 3.6+ is installed on your system
3. Install required Python packages:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install Pillow pytesseract
```

### Receipt Scanning Setup (Optional)

To use the receipt scanning feature, install Tesseract OCR:

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

The app will work without Tesseract, but receipt scanning will not be available.

## Usage

### Running the Application

```bash
python accounting_app.py
```

### Using the Application

#### Dashboard
- View your financial summary at a glance
- Quick access buttons to common actions
- Displays total income, total expenses, and net balance

#### Adding Transactions

**Manual Entry:**
1. Navigate to the "Add Transaction" tab
2. Select transaction type (Income or Expense)
3. Enter the date in YYYY-MM-DD format
4. Choose a category from the dropdown
5. Enter the amount (positive number)
6. Optionally add a description
7. Click "Add Transaction"

**Receipt Scanning (Auto-fill):**
1. Navigate to the "Add Transaction" tab
2. Click "Select Receipt Image" button
3. Choose a receipt image (JPG, PNG, etc.)
4. The app will automatically extract and fill in:
   - Transaction date
   - Amount paid
   - Merchant name (as description)
   - Suggested category based on merchant type
5. Review the auto-filled information
6. Make any necessary adjustments
7. Click "Add Transaction"

**Supported Receipt Image Formats:**
- PNG, JPG, JPEG, GIF, BMP, TIFF
- Clear, well-lit images work best
- Avoid blurry or skewed images

**Income Categories:**
- Salary
- Freelance
- Investment
- Gift
- Refund
- Other

**Expense Categories:**
- Groceries
- Utilities
- Rent
- Transportation
- Entertainment
- Healthcare
- Education
- Dining
- Shopping
- Other

#### Viewing Transactions

1. Navigate to the "Transactions" tab
2. View all transactions in a sortable table
3. Select a transaction and click "Delete Selected" to remove it
4. Click "Refresh" to update the list

#### Generating Reports

1. Navigate to the "Reports" tab
2. Choose report type:
   - **Summary Report**: Overview with category breakdowns
   - **Detailed Transactions**: Complete transaction listing
3. Optionally specify a date range
4. Click "Generate Report" to view
5. Click "Export to File" to save the report

## File Structure

```
accounting_app/
├── accounting_app.py    # Main GUI application
├── database.py          # Database operations and queries
├── reports.py           # Report generation functionality
├── receipt_parser.py    # OCR-based receipt scanning
├── test_app.py          # Test suite
├── accounting.db        # SQLite database (created on first run)
└── README.md           # This file
```

## Database Schema

The application uses a single SQLite table for transactions:

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    category TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    description TEXT
)
```

## Features in Detail

### Database Module (database.py)

The `AccountingDB` class provides:
- Transaction CRUD operations
- Query methods for filtering by type, date range
- Aggregation functions for totals and balances
- Category-based grouping and analysis

### Reports Module (reports.py)

The `ReportGenerator` class provides:
- Summary reports with category breakdowns
- Detailed transaction listings
- Percentage calculations
- File export functionality

### Receipt Parser Module (receipt_parser.py)

The `ReceiptParser` class provides:
- OCR text extraction from receipt images using Tesseract
- Intelligent parsing of:
  - Total amount (handles multiple currency formats)
  - Transaction date (supports various date formats)
  - Merchant name (extracted from top of receipt)
- Smart category suggestion based on merchant/keywords
- Graceful error handling when OCR is unavailable

### GUI Application (accounting_app.py)

The `AccountingApp` class provides:
- Tabbed interface with four main sections
- Real-time data validation
- Automatic summary updates
- Transaction management with confirmation dialogs

## Tips

- Use consistent date format (YYYY-MM-DD) for proper chronological sorting
- Review the dashboard regularly to track your financial health
- Generate monthly reports to analyze spending patterns
- Back up the `accounting.db` file periodically

## Customization

You can customize the application by:
- Modifying category lists in `accounting_app.py` (lines ~35-42)
- Adjusting the GUI layout and colors
- Adding new report types in `reports.py`
- Extending the database schema for additional features

## Troubleshooting

**Issue: "No module named 'tkinter'"**
- On Ubuntu/Debian: `sudo apt-install python3-tk`
- On Fedora: `sudo dnf install python3-tkinter`
- On macOS: tkinter should be included with Python

**Issue: Database locked error**
- Close any other instances of the application
- Ensure you have write permissions in the application directory

## Future Enhancements

Possible features for future versions:
- Budget tracking and alerts
- Recurring transactions
- Multiple account support
- Data visualization with charts
- CSV import/export
- Password protection
- Cloud backup integration

## License

This project is provided as-is for personal use and learning purposes.

## Author

Created with Python, tkinter, and SQLite.
