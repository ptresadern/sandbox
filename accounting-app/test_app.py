"""
Test script for the accounting application.
Tests database and reports functionality.
"""

import os
from datetime import datetime
from database import AccountingDB
from reports import ReportGenerator


def test_database():
    """Test database operations."""
    print("Testing database operations...")

    # Use a test database
    test_db = "test_accounting.db"

    # Clean up if exists
    if os.path.exists(test_db):
        os.remove(test_db)

    # Create database
    db = AccountingDB(test_db)
    print("✓ Database created successfully")

    # Add income transaction
    trans_id1 = db.add_transaction(
        date="2025-01-15",
        trans_type="income",
        category="Salary",
        amount=5000.00,
        description="Monthly salary"
    )
    print(f"✓ Income transaction added (ID: {trans_id1})")

    # Add expense transaction
    trans_id2 = db.add_transaction(
        date="2025-01-16",
        trans_type="expense",
        category="Groceries",
        amount=150.50,
        description="Weekly groceries"
    )
    print(f"✓ Expense transaction added (ID: {trans_id2})")

    # Add another expense
    trans_id3 = db.add_transaction(
        date="2025-01-17",
        trans_type="expense",
        category="Utilities",
        amount=200.00,
        description="Electric bill"
    )
    print(f"✓ Another expense transaction added (ID: {trans_id3})")

    # Test retrieving all transactions
    all_trans = db.get_all_transactions()
    assert len(all_trans) == 3, f"Expected 3 transactions, got {len(all_trans)}"
    print(f"✓ Retrieved all transactions: {len(all_trans)}")

    # Test retrieving by type
    income_trans = db.get_transactions_by_type("income")
    assert len(income_trans) == 1, f"Expected 1 income transaction, got {len(income_trans)}"
    print(f"✓ Retrieved income transactions: {len(income_trans)}")

    expense_trans = db.get_transactions_by_type("expense")
    assert len(expense_trans) == 2, f"Expected 2 expense transactions, got {len(expense_trans)}"
    print(f"✓ Retrieved expense transactions: {len(expense_trans)}")

    # Test totals
    total_income = db.get_total_income()
    assert total_income == 5000.00, f"Expected income 5000.00, got {total_income}"
    print(f"✓ Total income: ${total_income:.2f}")

    total_expenses = db.get_total_expenses()
    assert total_expenses == 350.50, f"Expected expenses 350.50, got {total_expenses}"
    print(f"✓ Total expenses: ${total_expenses:.2f}")

    balance = db.get_balance()
    expected_balance = 4649.50
    assert balance == expected_balance, f"Expected balance {expected_balance}, got {balance}"
    print(f"✓ Net balance: ${balance:.2f}")

    # Test category grouping
    expenses_by_cat = db.get_expenses_by_category()
    assert len(expenses_by_cat) == 2, f"Expected 2 expense categories, got {len(expenses_by_cat)}"
    print(f"✓ Expenses by category: {expenses_by_cat}")

    # Test deletion
    deleted = db.delete_transaction(trans_id2)
    assert deleted, "Failed to delete transaction"
    print(f"✓ Transaction deleted (ID: {trans_id2})")

    remaining = db.get_all_transactions()
    assert len(remaining) == 2, f"Expected 2 remaining transactions, got {len(remaining)}"
    print(f"✓ Remaining transactions: {len(remaining)}")

    # Clean up
    if os.path.exists(test_db):
        os.remove(test_db)
    print("✓ Test database cleaned up")

    print("\n✅ All database tests passed!\n")
    return db


def test_reports():
    """Test report generation."""
    print("Testing report generation...")

    # Use a test database
    test_db = "test_accounting.db"

    # Clean up if exists
    if os.path.exists(test_db):
        os.remove(test_db)

    # Create database and add sample data
    db = AccountingDB(test_db)

    # Add multiple transactions
    db.add_transaction("2025-01-01", "income", "Salary", 5000.00, "January salary")
    db.add_transaction("2025-01-05", "expense", "Rent", 1500.00, "Monthly rent")
    db.add_transaction("2025-01-10", "expense", "Groceries", 300.00, "Food shopping")
    db.add_transaction("2025-01-15", "expense", "Utilities", 200.00, "Electric and water")
    db.add_transaction("2025-01-20", "income", "Freelance", 1000.00, "Web project")
    db.add_transaction("2025-01-25", "expense", "Entertainment", 150.00, "Movies and dining")

    print("✓ Sample data created")

    # Create report generator
    report_gen = ReportGenerator(db)

    # Generate summary report
    summary_report = report_gen.generate_summary_report()
    assert len(summary_report) > 0, "Summary report is empty"
    assert "FINANCIAL SUMMARY REPORT" in summary_report, "Summary report missing title"
    assert "Total Income" in summary_report, "Summary report missing income"
    assert "Total Expenses" in summary_report, "Summary report missing expenses"
    print("✓ Summary report generated")

    # Generate transactions report
    trans_report = report_gen.generate_transactions_report()
    assert len(trans_report) > 0, "Transactions report is empty"
    assert "DETAILED TRANSACTIONS REPORT" in trans_report, "Transactions report missing title"
    print("✓ Transactions report generated")

    # Test date range reports
    range_report = report_gen.generate_summary_report("2025-01-01", "2025-01-15")
    assert "2025-01-01 to 2025-01-15" in range_report, "Date range not in report"
    print("✓ Date range report generated")

    # Test export
    test_report_file = "test_report.txt"
    success = report_gen.export_report_to_file(summary_report, test_report_file)
    assert success, "Failed to export report"
    assert os.path.exists(test_report_file), "Report file not created"
    print(f"✓ Report exported to {test_report_file}")

    # Print sample report
    print("\n" + "="*60)
    print("SAMPLE SUMMARY REPORT:")
    print("="*60)
    print(summary_report)
    print("="*60 + "\n")

    # Clean up
    if os.path.exists(test_db):
        os.remove(test_db)
    if os.path.exists(test_report_file):
        os.remove(test_report_file)
    print("✓ Test files cleaned up")

    print("\n✅ All report tests passed!\n")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("Testing edge cases...")

    test_db = "test_accounting.db"

    # Clean up if exists
    if os.path.exists(test_db):
        os.remove(test_db)

    db = AccountingDB(test_db)

    # Test empty database
    total_income = db.get_total_income()
    assert total_income == 0.0, f"Expected 0 income for empty DB, got {total_income}"
    print("✓ Empty database returns 0 for totals")

    balance = db.get_balance()
    assert balance == 0.0, f"Expected 0 balance for empty DB, got {balance}"
    print("✓ Empty database returns 0 for balance")

    all_trans = db.get_all_transactions()
    assert len(all_trans) == 0, f"Expected 0 transactions for empty DB, got {len(all_trans)}"
    print("✓ Empty database returns empty list")

    # Test deleting non-existent transaction
    deleted = db.delete_transaction(999)
    assert not deleted, "Should return False when deleting non-existent transaction"
    print("✓ Deleting non-existent transaction returns False")

    # Clean up
    if os.path.exists(test_db):
        os.remove(test_db)

    print("\n✅ All edge case tests passed!\n")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("RUNNING ACCOUNTING APP TESTS")
    print("="*60 + "\n")

    try:
        test_database()
        test_reports()
        test_edge_cases()

        print("="*60)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("="*60)
        print("\nThe accounting application is ready to use.")
        print("Run 'python accounting_app.py' to start the GUI.\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
