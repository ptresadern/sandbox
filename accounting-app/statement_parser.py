"""
Bank statement parser module for extracting transaction data from PDF statements.
Supports bulk import of transactions from bank statements.
"""

import re
from datetime import datetime
from typing import List, Dict, Optional
try:
    from PyPDF2 import PdfReader
except ImportError:
    # Try old import name
    from PyPDF2 import PdfFileReader as PdfReader


class BankStatementParser:
    """Parses PDF bank statements to extract transaction data."""

    def __init__(self):
        """Initialize the bank statement parser."""
        pass

    def extract_account_number(self, text: str) -> Optional[str]:
        """
        Extract account number from bank statement text.

        Args:
            text: Full text from bank statement

        Returns:
            Account number if found, None otherwise
        """
        # Common patterns for account numbers
        patterns = [
            r'account\s+(?:number|no\.?|#)\s*[:.]?\s*(\d[\d\s-]{8,20})',
            r'a/c\s+(?:number|no\.?)\s*[:.]?\s*(\d[\d\s-]{8,20})',
            r'account[:.]?\s+(\d[\d\s-]{8,20})',
            r'(\d{8,20})',  # Fallback: any long number sequence
        ]

        text_lower = text.lower()

        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                account_num = match.group(1)
                # Clean up the account number
                account_num = re.sub(r'\s+', '', account_num)
                if len(account_num) >= 8:
                    return account_num

        return None

    def extract_statement_period(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract statement period dates.

        Args:
            text: Full text from bank statement

        Returns:
            Dictionary with 'start_date' and 'end_date'
        """
        result = {'start_date': None, 'end_date': None}

        # Look for statement period
        patterns = [
            r'statement\s+period[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(?:to|through|-)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'period[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(?:to|through|-)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'from\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+to\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]

        text_lower = text.lower()

        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                result['start_date'] = self.parse_date(match.group(1))
                result['end_date'] = self.parse_date(match.group(2))
                break

        return result

    def parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse a date string and convert to YYYY-MM-DD format.

        Args:
            date_str: Date string to parse

        Returns:
            Date in YYYY-MM-DD format, or None if parsing fails
        """
        # List of date formats to try
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m-%d-%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%m-%d-%y",
            "%m/%d/%y",
            "%d-%m-%y",
            "%d/%m/%y",
            "%b %d, %Y",
            "%B %d, %Y",
            "%d %b %Y",
            "%d %B %Y",
            "%d-%b-%Y",
            "%d-%b-%y",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return None

    def clean_amount(self, amount_str: str) -> Optional[float]:
        """
        Clean and convert amount string to float.

        Args:
            amount_str: Amount string (e.g., "$1,234.56", "1234.56-", etc.)

        Returns:
            Float amount, or None if invalid
        """
        if not amount_str or amount_str.strip() in ['', '-', 'N/A']:
            return None

        # Remove currency symbols and spaces
        cleaned = re.sub(r'[$£€¥,\s]', '', amount_str.strip())

        # Check if it's a negative amount (ends with -, or in parentheses)
        is_negative = False
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = cleaned[1:-1]
            is_negative = True
        elif cleaned.endswith('-'):
            cleaned = cleaned[:-1]
            is_negative = True
        elif cleaned.startswith('-'):
            is_negative = True
            cleaned = cleaned[1:]

        try:
            amount = float(cleaned)
            return -amount if is_negative else amount
        except ValueError:
            return None

    def extract_transactions_from_table(self, table: List[List[str]],
                                       account_number: Optional[str]) -> List[Dict]:
        """
        Extract transactions from a table structure.

        Args:
            table: List of rows, each row is a list of cells
            account_number: Account number for the transactions

        Returns:
            List of transaction dictionaries
        """
        if not table or len(table) < 2:
            return []

        transactions = []

        # Try to identify column headers
        header_row = table[0]
        header_lower = [str(cell).lower() if cell else '' for cell in header_row]

        # Find column indices
        date_col = None
        desc_col = None
        debit_col = None
        credit_col = None
        amount_col = None

        for i, header in enumerate(header_lower):
            if 'date' in header:
                date_col = i
            elif 'description' in header or 'payee' in header or 'details' in header:
                desc_col = i
            elif 'debit' in header or 'withdrawal' in header or 'payment' in header:
                debit_col = i
            elif 'credit' in header or 'deposit' in header:
                credit_col = i
            elif 'amount' in header:
                amount_col = i

        # If we couldn't find headers, try to guess based on common positions
        if date_col is None:
            date_col = 0  # Date is usually first column
        if desc_col is None:
            desc_col = 1  # Description is usually second

        # Process each row
        for row in table[1:]:
            if not row or len(row) < 2:
                continue

            # Skip header rows that might appear mid-table
            row_lower = [str(cell).lower() if cell else '' for cell in row]
            if any('date' in cell for cell in row_lower):
                continue

            try:
                # Extract date
                date_str = str(row[date_col]) if date_col < len(row) else ''
                transaction_date = self.parse_date(date_str)

                if not transaction_date:
                    continue

                # Extract description/payee
                description = str(row[desc_col]) if desc_col < len(row) else ''
                description = description.strip()

                if not description or description.lower() in ['', 'n/a', 'none']:
                    continue

                # Extract amount
                amount = None
                trans_type = 'expense'

                # Try to get amount from debit/credit columns
                if debit_col is not None and debit_col < len(row):
                    debit_amount = self.clean_amount(str(row[debit_col]))
                    if debit_amount and debit_amount != 0:
                        amount = abs(debit_amount)
                        trans_type = 'expense'

                if amount is None and credit_col is not None and credit_col < len(row):
                    credit_amount = self.clean_amount(str(row[credit_col]))
                    if credit_amount and credit_amount != 0:
                        amount = abs(credit_amount)
                        trans_type = 'income'

                # Try amount column if debit/credit didn't work
                if amount is None and amount_col is not None and amount_col < len(row):
                    amt = self.clean_amount(str(row[amount_col]))
                    if amt and amt != 0:
                        if amt < 0:
                            amount = abs(amt)
                            trans_type = 'expense'
                        else:
                            amount = amt
                            trans_type = 'income'

                if amount is None or amount == 0:
                    continue

                # Create transaction record
                transaction = {
                    'date': transaction_date,
                    'description': description,
                    'amount': amount,
                    'type': trans_type,
                    'account_number': account_number,
                    'category': 'Other',  # Default category
                }

                transactions.append(transaction)

            except Exception as e:
                # Skip problematic rows
                continue

        return transactions

    def extract_transactions_from_text(self, text: str,
                                      account_number: Optional[str]) -> List[Dict]:
        """
        Extract transactions from plain text using regex patterns.

        Args:
            text: Text from PDF
            account_number: Account number for the transactions

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        # Pattern to match transaction lines
        # Format: DATE DESCRIPTION AMOUNT
        # Common patterns:
        # 01/15/2024 WALMART #1234 -45.67
        # 2024-01-15 AMAZON.COM 123.45
        # Jan 15 STARBUCKS -5.50

        pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2})\s+([a-z0-9\s\.\#\-\*\'&]+?)\s+([-]?\$?\s*[\d,]+\.?\d{0,2})\s*(?:[-]?\$?\s*[\d,]+\.?\d{0,2})?\s*$'

        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip header lines
            if any(keyword in line.lower() for keyword in ['date', 'description', 'amount', 'balance', 'beginning', 'ending']):
                continue

            match = re.search(pattern, line, re.IGNORECASE)

            if match:
                date_str = match.group(1)
                description = match.group(2).strip()
                amount_str = match.group(3)

                # Parse date
                transaction_date = self.parse_date(date_str)
                if not transaction_date:
                    continue

                # Clean description
                if not description or len(description) < 2:
                    continue

                # Parse amount
                amount = self.clean_amount(amount_str)
                if amount is None or amount == 0:
                    continue

                # Determine type
                if amount < 0:
                    trans_type = 'expense'
                    amount = abs(amount)
                else:
                    trans_type = 'income'

                transaction = {
                    'date': transaction_date,
                    'description': description,
                    'amount': amount,
                    'type': trans_type,
                    'account_number': account_number,
                    'category': self.suggest_category(description),
                }

                transactions.append(transaction)

        return transactions

    def parse_statement(self, pdf_path: str) -> Dict:
        """
        Parse a bank statement PDF and extract transaction data.

        Args:
            pdf_path: Path to the PDF bank statement

        Returns:
            Dictionary with:
            {
                'account_number': str or None,
                'statement_period': {'start_date': str, 'end_date': str},
                'transactions': List[Dict],
                'success': bool,
                'error': str or None
            }
        """
        result = {
            'account_number': None,
            'statement_period': {'start_date': None, 'end_date': None},
            'transactions': [],
            'success': False,
            'error': None
        }

        try:
            # Read PDF using PyPDF2
            reader = PdfReader(pdf_path)

            # Extract text from all pages
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"

            if not full_text or len(full_text.strip()) < 50:
                result['error'] = "Could not extract text from PDF. The file may be image-based or encrypted."
                return result

            # Extract account number from first page
            result['account_number'] = self.extract_account_number(full_text)

            # Extract statement period
            result['statement_period'] = self.extract_statement_period(full_text)

            # Extract transactions from text
            transactions = self.extract_transactions_from_text(full_text, result['account_number'])

            result['transactions'] = transactions

            if len(transactions) > 0:
                result['success'] = True
            else:
                result['error'] = "No transactions found in the statement. The PDF format may not be supported."

        except FileNotFoundError:
            result['error'] = f"PDF file not found: {pdf_path}"
        except Exception as e:
            result['error'] = f"Error parsing bank statement: {str(e)}"

        return result

    def suggest_category(self, description: str) -> str:
        """
        Suggest a category based on transaction description.

        Args:
            description: Transaction description/payee

        Returns:
            Suggested category name
        """
        desc_lower = description.lower()

        # Category keywords mapping (same as receipt parser)
        category_keywords = {
            'Groceries': ['grocery', 'supermarket', 'market', 'food', 'walmart', 'target',
                         'whole foods', 'trader joe', 'safeway', 'kroger', 'costco'],
            'Dining': ['restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'food',
                      'dining', 'starbucks', 'mcdonald', 'subway', 'diner', 'bar'],
            'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'transit',
                             'parking', 'chevron', 'shell', 'bp', '76', 'exxon'],
            'Utilities': ['electric', 'water', 'gas', 'utility', 'power', 'energy',
                         'phone', 'internet', 'cable', 'verizon', 'att', 'comcast'],
            'Entertainment': ['movie', 'cinema', 'theater', 'netflix', 'spotify',
                            'game', 'entertainment', 'amusement', 'ticket'],
            'Healthcare': ['pharmacy', 'medical', 'doctor', 'hospital', 'health',
                          'cvs', 'walgreens', 'clinic', 'dental'],
            'Shopping': ['store', 'shop', 'retail', 'amazon', 'ebay', 'mall',
                        'clothing', 'fashion', 'best buy'],
            'Rent': ['rent', 'lease', 'housing', 'apartment', 'property'],
            'Salary': ['salary', 'payroll', 'wage', 'income', 'employer', 'direct deposit'],
            'Refund': ['refund', 'return', 'reimbursement'],
        }

        # Check for category matches
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    return category

        # Default category
        return 'Other'


def test_statement_parser():
    """Test function for bank statement parser."""
    parser = BankStatementParser()
    print("✓ Bank statement parser initialized successfully")
    print("Ready to parse PDF bank statements")
    return True


if __name__ == "__main__":
    test_statement_parser()
