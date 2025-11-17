"""
Reports module for generating financial summaries.
"""

from datetime import datetime
from typing import Optional
from database import AccountingDB


class ReportGenerator:
    """Generates financial reports from transaction data."""

    def __init__(self, db: AccountingDB):
        """Initialize with database instance."""
        self.db = db

    def generate_summary_report(self, start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> str:
        """
        Generate a summary financial report.

        Args:
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            Formatted report string
        """
        total_income = self.db.get_total_income(start_date, end_date)
        total_expenses = self.db.get_total_expenses(start_date, end_date)
        balance = self.db.get_balance(start_date, end_date)

        # Get category breakdowns
        income_by_category = self.db.get_income_by_category(start_date, end_date)
        expenses_by_category = self.db.get_expenses_by_category(start_date, end_date)

        # Build report
        report = []
        report.append("=" * 60)
        report.append("FINANCIAL SUMMARY REPORT")
        report.append("=" * 60)

        if start_date and end_date:
            report.append(f"Period: {start_date} to {end_date}")
        else:
            report.append("Period: All Time")

        report.append("")
        report.append("-" * 60)
        report.append("OVERVIEW")
        report.append("-" * 60)
        report.append(f"Total Income:        ${total_income:,.2f}")
        report.append(f"Total Expenses:      ${total_expenses:,.2f}")
        report.append(f"Net Balance:         ${balance:,.2f}")
        report.append("")

        # Income breakdown
        if income_by_category:
            report.append("-" * 60)
            report.append("INCOME BY CATEGORY")
            report.append("-" * 60)
            for category, amount in income_by_category:
                percentage = (amount / total_income * 100) if total_income > 0 else 0
                report.append(f"{category:.<30} ${amount:>10,.2f} ({percentage:>5.1f}%)")
            report.append("")

        # Expenses breakdown
        if expenses_by_category:
            report.append("-" * 60)
            report.append("EXPENSES BY CATEGORY")
            report.append("-" * 60)
            for category, amount in expenses_by_category:
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                report.append(f"{category:.<30} ${amount:>10,.2f} ({percentage:>5.1f}%)")
            report.append("")

        report.append("=" * 60)
        report.append(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)

        return "\n".join(report)

    def generate_transactions_report(self, start_date: Optional[str] = None,
                                    end_date: Optional[str] = None) -> str:
        """
        Generate a detailed transactions report.

        Args:
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            Formatted report string
        """
        if start_date and end_date:
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.db.get_all_transactions()

        report = []
        report.append("=" * 80)
        report.append("DETAILED TRANSACTIONS REPORT")
        report.append("=" * 80)

        if start_date and end_date:
            report.append(f"Period: {start_date} to {end_date}")
        else:
            report.append("Period: All Time")

        report.append("")
        report.append(f"Total Transactions: {len(transactions)}")
        report.append("")

        if transactions:
            report.append("-" * 80)
            report.append(f"{'Date':<12} {'Type':<10} {'Category':<20} {'Amount':>12} {'Description':<20}")
            report.append("-" * 80)

            for trans in transactions:
                trans_type = trans['type'].upper()
                amount = trans['amount']
                # Format amount with sign
                if trans['type'] == 'expense':
                    amount_str = f"-${amount:,.2f}"
                else:
                    amount_str = f"+${amount:,.2f}"

                description = trans['description'][:20] if trans['description'] else ""

                report.append(
                    f"{trans['date']:<12} "
                    f"{trans_type:<10} "
                    f"{trans['category']:<20} "
                    f"{amount_str:>12} "
                    f"{description:<20}"
                )

        report.append("-" * 80)
        report.append(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)

        return "\n".join(report)

    def export_report_to_file(self, report: str, filename: str) -> bool:
        """
        Export a report to a text file.

        Args:
            report: Report string to export
            filename: Output filename

        Returns:
            True if successful
        """
        try:
            with open(filename, 'w') as f:
                f.write(report)
            return True
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False
