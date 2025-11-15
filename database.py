"""
Database module for the accounting application.
Handles SQLite database operations for transactions.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class AccountingDB:
    """Manages database operations for the accounting application."""

    def __init__(self, db_name: str = "accounting.db"):
        """Initialize database connection and create tables if needed."""
        self.db_name = db_name
        self.conn = None
        self.create_tables()

    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Create necessary tables if they don't exist."""
        conn = self.connect()
        cursor = conn.cursor()

        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                description TEXT
            )
        ''')

        conn.commit()
        self.close()

    def add_transaction(self, date: str, trans_type: str, category: str,
                       amount: float, description: str = "") -> int:
        """
        Add a new transaction to the database.

        Args:
            date: Transaction date (YYYY-MM-DD format)
            trans_type: 'income' or 'expense'
            category: Transaction category
            amount: Transaction amount (positive number)
            description: Optional description

        Returns:
            ID of the inserted transaction
        """
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO transactions (date, type, category, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, trans_type, category, amount, description))

        trans_id = cursor.lastrowid
        conn.commit()
        self.close()

        return trans_id

    def get_all_transactions(self, order_by: str = "date DESC") -> List[Dict]:
        """
        Retrieve all transactions from the database.

        Args:
            order_by: SQL ORDER BY clause

        Returns:
            List of transaction dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(f'''
            SELECT id, date, type, category, amount, description
            FROM transactions
            ORDER BY {order_by}
        ''')

        transactions = [dict(row) for row in cursor.fetchall()]
        self.close()

        return transactions

    def get_transactions_by_type(self, trans_type: str) -> List[Dict]:
        """Get all transactions of a specific type."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, date, type, category, amount, description
            FROM transactions
            WHERE type = ?
            ORDER BY date DESC
        ''', (trans_type,))

        transactions = [dict(row) for row in cursor.fetchall()]
        self.close()

        return transactions

    def get_transactions_by_date_range(self, start_date: str,
                                       end_date: str) -> List[Dict]:
        """Get transactions within a date range."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, date, type, category, amount, description
            FROM transactions
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
        ''', (start_date, end_date))

        transactions = [dict(row) for row in cursor.fetchall()]
        self.close()

        return transactions

    def delete_transaction(self, trans_id: int) -> bool:
        """
        Delete a transaction by ID.

        Args:
            trans_id: Transaction ID to delete

        Returns:
            True if deletion was successful
        """
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM transactions WHERE id = ?', (trans_id,))

        success = cursor.rowcount > 0
        conn.commit()
        self.close()

        return success

    def get_total_income(self, start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> float:
        """Calculate total income, optionally within a date range."""
        conn = self.connect()
        cursor = conn.cursor()

        if start_date and end_date:
            cursor.execute('''
                SELECT SUM(amount) FROM transactions
                WHERE type = 'income' AND date BETWEEN ? AND ?
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT SUM(amount) FROM transactions
                WHERE type = 'income'
            ''')

        result = cursor.fetchone()[0]
        self.close()

        return result if result else 0.0

    def get_total_expenses(self, start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> float:
        """Calculate total expenses, optionally within a date range."""
        conn = self.connect()
        cursor = conn.cursor()

        if start_date and end_date:
            cursor.execute('''
                SELECT SUM(amount) FROM transactions
                WHERE type = 'expense' AND date BETWEEN ? AND ?
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT SUM(amount) FROM transactions
                WHERE type = 'expense'
            ''')

        result = cursor.fetchone()[0]
        self.close()

        return result if result else 0.0

    def get_balance(self, start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> float:
        """Calculate balance (income - expenses)."""
        income = self.get_total_income(start_date, end_date)
        expenses = self.get_total_expenses(start_date, end_date)
        return income - expenses

    def get_expenses_by_category(self, start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> List[Tuple[str, float]]:
        """Get expenses grouped by category."""
        conn = self.connect()
        cursor = conn.cursor()

        if start_date and end_date:
            cursor.execute('''
                SELECT category, SUM(amount) as total
                FROM transactions
                WHERE type = 'expense' AND date BETWEEN ? AND ?
                GROUP BY category
                ORDER BY total DESC
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT category, SUM(amount) as total
                FROM transactions
                WHERE type = 'expense'
                GROUP BY category
                ORDER BY total DESC
            ''')

        results = cursor.fetchall()
        self.close()

        return [(row[0], row[1]) for row in results]

    def get_income_by_category(self, start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> List[Tuple[str, float]]:
        """Get income grouped by category."""
        conn = self.connect()
        cursor = conn.cursor()

        if start_date and end_date:
            cursor.execute('''
                SELECT category, SUM(amount) as total
                FROM transactions
                WHERE type = 'income' AND date BETWEEN ? AND ?
                GROUP BY category
                ORDER BY total DESC
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT category, SUM(amount) as total
                FROM transactions
                WHERE type = 'income'
                GROUP BY category
                ORDER BY total DESC
            ''')

        results = cursor.fetchall()
        self.close()

        return [(row[0], row[1]) for row in results]
