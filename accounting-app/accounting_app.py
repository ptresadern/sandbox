"""
Main accounting application with tkinter GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime
from database import AccountingDB
from reports import ReportGenerator
from receipt_parser import ReceiptParser
from statement_parser import BankStatementParser


class AccountingApp:
    """Main application class for the accounting GUI."""

    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("Personal Accounting App")
        self.root.geometry("1000x700")

        # Initialize database and reports
        self.db = AccountingDB()
        self.report_gen = ReportGenerator(self.db)
        self.receipt_parser = ReceiptParser()
        self.statement_parser = BankStatementParser()

        # Common categories
        self.income_categories = [
            "Salary", "Freelance", "Investment", "Gift", "Refund", "Other"
        ]
        self.expense_categories = [
            "Groceries", "Utilities", "Rent", "Transportation", "Entertainment",
            "Healthcare", "Education", "Dining", "Shopping", "Other"
        ]

        # Create GUI
        self.create_widgets()
        self.refresh_transaction_list()
        self.update_summary()

    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.create_dashboard_tab()
        self.create_add_transaction_tab()
        self.create_import_statement_tab()
        self.create_transactions_tab()
        self.create_reports_tab()

    def create_dashboard_tab(self):
        """Create dashboard tab with summary statistics."""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")

        # Title
        title_label = tk.Label(
            dashboard_frame,
            text="Financial Dashboard",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # Summary frame
        summary_frame = ttk.LabelFrame(dashboard_frame, text="Summary", padding=20)
        summary_frame.pack(fill='x', padx=20, pady=10)

        # Summary labels
        self.total_income_label = tk.Label(
            summary_frame,
            text="Total Income: $0.00",
            font=("Arial", 12)
        )
        self.total_income_label.grid(row=0, column=0, sticky='w', pady=5)

        self.total_expenses_label = tk.Label(
            summary_frame,
            text="Total Expenses: $0.00",
            font=("Arial", 12)
        )
        self.total_expenses_label.grid(row=1, column=0, sticky='w', pady=5)

        self.balance_label = tk.Label(
            summary_frame,
            text="Net Balance: $0.00",
            font=("Arial", 14, "bold")
        )
        self.balance_label.grid(row=2, column=0, sticky='w', pady=10)

        # Quick actions frame
        actions_frame = ttk.LabelFrame(dashboard_frame, text="Quick Actions", padding=20)
        actions_frame.pack(fill='x', padx=20, pady=10)

        ttk.Button(
            actions_frame,
            text="Add Income",
            command=lambda: self.switch_to_add_transaction("income")
        ).grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(
            actions_frame,
            text="Add Expense",
            command=lambda: self.switch_to_add_transaction("expense")
        ).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(
            actions_frame,
            text="View Transactions",
            command=lambda: self.notebook.select(2)
        ).grid(row=0, column=2, padx=5, pady=5)

        ttk.Button(
            actions_frame,
            text="Generate Report",
            command=lambda: self.notebook.select(3)
        ).grid(row=0, column=3, padx=5, pady=5)

        # Refresh button
        ttk.Button(
            dashboard_frame,
            text="Refresh Dashboard",
            command=self.update_summary
        ).pack(pady=10)

    def create_add_transaction_tab(self):
        """Create tab for adding new transactions."""
        add_frame = ttk.Frame(self.notebook)
        self.notebook.add(add_frame, text="Add Transaction")

        # Title
        title_label = tk.Label(
            add_frame,
            text="Add New Transaction",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)

        # Form frame
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(padx=20, pady=10)

        # Transaction type
        ttk.Label(form_frame, text="Type:").grid(row=0, column=0, sticky='w', pady=5)
        self.trans_type_var = tk.StringVar(value="expense")
        type_frame = ttk.Frame(form_frame)
        type_frame.grid(row=0, column=1, sticky='w', pady=5)
        ttk.Radiobutton(
            type_frame,
            text="Income",
            variable=self.trans_type_var,
            value="income",
            command=self.update_category_list
        ).pack(side='left', padx=5)
        ttk.Radiobutton(
            type_frame,
            text="Expense",
            variable=self.trans_type_var,
            value="expense",
            command=self.update_category_list
        ).pack(side='left', padx=5)

        # Date
        ttk.Label(form_frame, text="Date:").grid(row=1, column=0, sticky='w', pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(form_frame, textvariable=self.date_var, width=30).grid(
            row=1, column=1, sticky='w', pady=5
        )
        ttk.Label(form_frame, text="(YYYY-MM-DD)").grid(row=1, column=2, sticky='w', pady=5)

        # Category
        ttk.Label(form_frame, text="Category:").grid(row=2, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            form_frame,
            textvariable=self.category_var,
            width=27
        )
        self.category_combo.grid(row=2, column=1, sticky='w', pady=5)
        self.update_category_list()

        # Amount
        ttk.Label(form_frame, text="Amount:").grid(row=3, column=0, sticky='w', pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.amount_var, width=30).grid(
            row=3, column=1, sticky='w', pady=5
        )

        # Description
        ttk.Label(form_frame, text="Description:").grid(row=4, column=0, sticky='w', pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.description_var, width=30).grid(
            row=4, column=1, sticky='w', pady=5
        )

        # Receipt scanning section
        receipt_frame = ttk.LabelFrame(add_frame, text="📷 Scan Receipt (Auto-fill)", padding=15)
        receipt_frame.pack(fill='x', padx=20, pady=10)

        ttk.Label(
            receipt_frame,
            text="Upload a receipt image to automatically extract transaction details"
        ).pack(pady=5)

        scan_button_frame = ttk.Frame(receipt_frame)
        scan_button_frame.pack(pady=5)

        ttk.Button(
            scan_button_frame,
            text="📁 Select Receipt Image",
            command=self.scan_receipt
        ).pack(side='left', padx=5)

        self.ocr_status_label = tk.Label(
            receipt_frame,
            text="",
            font=("Arial", 9),
            fg="gray"
        )
        self.ocr_status_label.pack(pady=5)

        # Buttons
        button_frame = ttk.Frame(add_frame)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="Add Transaction",
            command=self.add_transaction
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="Clear Form",
            command=self.clear_form
        ).pack(side='left', padx=5)

    def create_import_statement_tab(self):
        """Create tab for importing bank statements."""
        import_frame = ttk.Frame(self.notebook)
        self.notebook.add(import_frame, text="Import Statement")

        # Title
        title_label = tk.Label(
            import_frame,
            text="Import Bank Statement",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)

        # Instructions
        instructions = ttk.LabelFrame(import_frame, text="Instructions", padding=15)
        instructions.pack(fill='x', padx=20, pady=10)

        ttk.Label(
            instructions,
            text="Upload a PDF bank statement to automatically import all transactions.\n"
                 "The app will extract: Date, Amount, Payee/Description, and Account Number.",
            font=("Arial", 10)
        ).pack(pady=5)

        # Upload section
        upload_frame = ttk.LabelFrame(import_frame, text="Upload Statement", padding=15)
        upload_frame.pack(fill='x', padx=20, pady=10)

        ttk.Button(
            upload_frame,
            text="📄 Select PDF Bank Statement",
            command=self.import_bank_statement
        ).pack(pady=10)

        self.import_status_label = tk.Label(
            upload_frame,
            text="",
            font=("Arial", 9),
            fg="gray"
        )
        self.import_status_label.pack(pady=5)

        # Preview frame
        preview_frame = ttk.LabelFrame(import_frame, text="Preview Transactions", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Treeview for preview
        tree_scroll = ttk.Scrollbar(preview_frame)
        tree_scroll.pack(side='right', fill='y')

        self.import_preview_tree = ttk.Treeview(
            preview_frame,
            columns=('Date', 'Description', 'Amount', 'Type', 'Category'),
            show='headings',
            yscrollcommand=tree_scroll.set
        )
        tree_scroll.config(command=self.import_preview_tree.yview)

        # Define columns
        self.import_preview_tree.heading('Date', text='Date')
        self.import_preview_tree.heading('Description', text='Description')
        self.import_preview_tree.heading('Amount', text='Amount')
        self.import_preview_tree.heading('Type', text='Type')
        self.import_preview_tree.heading('Category', text='Category')

        # Set column widths
        self.import_preview_tree.column('Date', width=100)
        self.import_preview_tree.column('Description', width=300)
        self.import_preview_tree.column('Amount', width=100)
        self.import_preview_tree.column('Type', width=80)
        self.import_preview_tree.column('Category', width=120)

        self.import_preview_tree.pack(fill='both', expand=True)

        # Import button
        import_button_frame = ttk.Frame(import_frame)
        import_button_frame.pack(pady=10)

        self.import_all_button = ttk.Button(
            import_button_frame,
            text="Import All Transactions",
            command=self.import_all_transactions,
            state='disabled'
        )
        self.import_all_button.pack(side='left', padx=5)

        ttk.Button(
            import_button_frame,
            text="Clear Preview",
            command=self.clear_import_preview
        ).pack(side='left', padx=5)

        # Store pending transactions
        self.pending_transactions = []

    def create_transactions_tab(self):
        """Create tab for viewing all transactions."""
        trans_frame = ttk.Frame(self.notebook)
        self.notebook.add(trans_frame, text="Transactions")

        # Title
        title_label = tk.Label(
            trans_frame,
            text="Transaction History",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)

        # Toolbar
        toolbar = ttk.Frame(trans_frame)
        toolbar.pack(fill='x', padx=10, pady=5)

        ttk.Button(
            toolbar,
            text="Refresh",
            command=self.refresh_transaction_list
        ).pack(side='left', padx=5)

        ttk.Button(
            toolbar,
            text="Delete Selected",
            command=self.delete_transaction
        ).pack(side='left', padx=5)

        # Treeview for transactions
        tree_frame = ttk.Frame(trans_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')

        # Create treeview
        self.trans_tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Date', 'Type', 'Category', 'Amount', 'Description'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.trans_tree.yview)

        # Define columns
        self.trans_tree.heading('ID', text='ID')
        self.trans_tree.heading('Date', text='Date')
        self.trans_tree.heading('Type', text='Type')
        self.trans_tree.heading('Category', text='Category')
        self.trans_tree.heading('Amount', text='Amount')
        self.trans_tree.heading('Description', text='Description')

        # Set column widths
        self.trans_tree.column('ID', width=50)
        self.trans_tree.column('Date', width=100)
        self.trans_tree.column('Type', width=80)
        self.trans_tree.column('Category', width=120)
        self.trans_tree.column('Amount', width=100)
        self.trans_tree.column('Description', width=300)

        self.trans_tree.pack(fill='both', expand=True)

    def create_reports_tab(self):
        """Create tab for generating reports."""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")

        # Title
        title_label = tk.Label(
            reports_frame,
            text="Financial Reports",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)

        # Options frame
        options_frame = ttk.LabelFrame(reports_frame, text="Report Options", padding=10)
        options_frame.pack(fill='x', padx=20, pady=10)

        # Report type
        ttk.Label(options_frame, text="Report Type:").grid(row=0, column=0, sticky='w', pady=5)
        self.report_type_var = tk.StringVar(value="summary")
        ttk.Radiobutton(
            options_frame,
            text="Summary Report",
            variable=self.report_type_var,
            value="summary"
        ).grid(row=0, column=1, sticky='w', pady=5)
        ttk.Radiobutton(
            options_frame,
            text="Detailed Transactions",
            variable=self.report_type_var,
            value="detailed"
        ).grid(row=0, column=2, sticky='w', pady=5)

        # Date range
        ttk.Label(options_frame, text="Date Range:").grid(row=1, column=0, sticky='w', pady=5)
        self.use_date_range_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Use Date Range",
            variable=self.use_date_range_var
        ).grid(row=1, column=1, sticky='w', pady=5)

        ttk.Label(options_frame, text="Start Date:").grid(row=2, column=0, sticky='w', pady=5)
        self.report_start_date_var = tk.StringVar()
        ttk.Entry(options_frame, textvariable=self.report_start_date_var, width=15).grid(
            row=2, column=1, sticky='w', pady=5
        )

        ttk.Label(options_frame, text="End Date:").grid(row=3, column=0, sticky='w', pady=5)
        self.report_end_date_var = tk.StringVar()
        ttk.Entry(options_frame, textvariable=self.report_end_date_var, width=15).grid(
            row=3, column=1, sticky='w', pady=5
        )

        # Buttons
        button_frame = ttk.Frame(reports_frame)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Generate Report",
            command=self.generate_report
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="Export to File",
            command=self.export_report
        ).pack(side='left', padx=5)

        # Report display
        report_frame = ttk.LabelFrame(reports_frame, text="Report Output", padding=10)
        report_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.report_text = scrolledtext.ScrolledText(
            report_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Courier", 9)
        )
        self.report_text.pack(fill='both', expand=True)

    def update_category_list(self):
        """Update category dropdown based on transaction type."""
        if self.trans_type_var.get() == "income":
            self.category_combo['values'] = self.income_categories
        else:
            self.category_combo['values'] = self.expense_categories

        # Set default value
        if self.category_combo['values']:
            self.category_var.set(self.category_combo['values'][0])

    def switch_to_add_transaction(self, trans_type):
        """Switch to add transaction tab with specified type."""
        self.trans_type_var.set(trans_type)
        self.update_category_list()
        self.notebook.select(1)

    def clear_form(self):
        """Clear the transaction form."""
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.amount_var.set("")
        self.description_var.set("")
        if self.category_combo['values']:
            self.category_var.set(self.category_combo['values'][0])

    def scan_receipt(self):
        """Scan a receipt image and auto-fill transaction fields."""
        # Update status
        self.ocr_status_label.config(text="Select a receipt image...", fg="gray")

        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Receipt Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            self.ocr_status_label.config(text="", fg="gray")
            return

        # Update status
        self.ocr_status_label.config(text="Processing receipt...", fg="blue")
        self.root.update()

        try:
            # Parse the receipt
            result = self.receipt_parser.parse_receipt(file_path)

            if result['error']:
                self.ocr_status_label.config(
                    text=f"Error: {result['error']}",
                    fg="red"
                )

                # Show detailed error message
                if "Tesseract" in result['error']:
                    messagebox.showwarning(
                        "OCR Not Available",
                        result['error'] + "\n\nThe receipt scanning feature requires "
                        "Tesseract OCR to be installed on your system."
                    )
                else:
                    messagebox.showerror("Scanning Error", result['error'])
                return

            # Auto-fill fields
            fields_filled = []

            if result['date']:
                self.date_var.set(result['date'])
                fields_filled.append("date")

            if result['amount']:
                self.amount_var.set(f"{result['amount']:.2f}")
                fields_filled.append("amount")

            if result['merchant']:
                # Use merchant name as description
                self.description_var.set(result['merchant'])
                fields_filled.append("description")

                # Try to suggest a category based on merchant
                suggested_category, suggested_type = self.receipt_parser.suggest_category(
                    result['merchant'],
                    result['raw_text']
                )

                # Set transaction type
                self.trans_type_var.set(suggested_type)
                self.update_category_list()

                # Set category
                if suggested_category:
                    self.category_var.set(suggested_category)
                    fields_filled.append("category")

            # Update status
            if fields_filled:
                status_msg = f"✓ Auto-filled: {', '.join(fields_filled)}"
                self.ocr_status_label.config(text=status_msg, fg="green")

                messagebox.showinfo(
                    "Receipt Scanned",
                    f"Successfully extracted data from receipt!\n\n"
                    f"Fields auto-filled: {', '.join(fields_filled)}\n\n"
                    f"Please review the information before adding the transaction."
                )
            else:
                self.ocr_status_label.config(
                    text="Could not extract data from receipt",
                    fg="orange"
                )
                messagebox.showwarning(
                    "Limited Data",
                    "Could not extract sufficient data from the receipt.\n"
                    "Please fill in the fields manually."
                )

        except Exception as e:
            self.ocr_status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Failed to scan receipt: {str(e)}")

    def add_transaction(self):
        """Add a new transaction to the database."""
        try:
            # Validate inputs
            date = self.date_var.get().strip()
            trans_type = self.trans_type_var.get()
            category = self.category_var.get().strip()
            amount_str = self.amount_var.get().strip()
            description = self.description_var.get().strip()

            if not date or not category or not amount_str:
                messagebox.showerror("Error", "Please fill in all required fields.")
                return

            # Validate date format
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                return

            # Validate amount
            try:
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount. Enter a positive number.")
                return

            # Add to database
            trans_id = self.db.add_transaction(
                date, trans_type, category, amount, description
            )

            messagebox.showinfo(
                "Success",
                f"Transaction added successfully! (ID: {trans_id})"
            )

            # Clear form and refresh
            self.clear_form()
            self.refresh_transaction_list()
            self.update_summary()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")

    def refresh_transaction_list(self):
        """Refresh the transaction list in the treeview."""
        # Clear existing items
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)

        # Get all transactions
        transactions = self.db.get_all_transactions()

        # Add to treeview
        for trans in transactions:
            amount_str = f"${trans['amount']:.2f}"
            if trans['type'] == 'expense':
                amount_str = f"-{amount_str}"
            else:
                amount_str = f"+{amount_str}"

            self.trans_tree.insert('', 'end', values=(
                trans['id'],
                trans['date'],
                trans['type'].capitalize(),
                trans['category'],
                amount_str,
                trans['description']
            ))

    def delete_transaction(self):
        """Delete the selected transaction."""
        selection = self.trans_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a transaction to delete.")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?"):
            return

        try:
            # Get transaction ID from selected item
            item = self.trans_tree.item(selection[0])
            trans_id = item['values'][0]

            # Delete from database
            if self.db.delete_transaction(trans_id):
                messagebox.showinfo("Success", "Transaction deleted successfully!")
                self.refresh_transaction_list()
                self.update_summary()
            else:
                messagebox.showerror("Error", "Failed to delete transaction.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete transaction: {str(e)}")

    def update_summary(self):
        """Update the dashboard summary statistics."""
        total_income = self.db.get_total_income()
        total_expenses = self.db.get_total_expenses()
        balance = self.db.get_balance()

        self.total_income_label.config(text=f"Total Income: ${total_income:,.2f}")
        self.total_expenses_label.config(text=f"Total Expenses: ${total_expenses:,.2f}")
        self.balance_label.config(
            text=f"Net Balance: ${balance:,.2f}",
            fg="green" if balance >= 0 else "red"
        )

    def generate_report(self):
        """Generate and display a financial report."""
        try:
            start_date = None
            end_date = None

            if self.use_date_range_var.get():
                start_date = self.report_start_date_var.get().strip()
                end_date = self.report_end_date_var.get().strip()

                if not start_date or not end_date:
                    messagebox.showerror("Error", "Please enter both start and end dates.")
                    return

                # Validate dates
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                    datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                    return

            # Generate report
            if self.report_type_var.get() == "summary":
                report = self.report_gen.generate_summary_report(start_date, end_date)
            else:
                report = self.report_gen.generate_transactions_report(start_date, end_date)

            # Display report
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(1.0, report)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

    def export_report(self):
        """Export the current report to a file."""
        report_content = self.report_text.get(1.0, tk.END).strip()

        if not report_content:
            messagebox.showwarning("Warning", "No report to export. Generate a report first.")
            return

        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_report_{timestamp}.txt"

            # Export report
            if self.report_gen.export_report_to_file(report_content, filename):
                messagebox.showinfo(
                    "Success",
                    f"Report exported successfully to:\n{filename}"
                )
            else:
                messagebox.showerror("Error", "Failed to export report.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")

    def import_bank_statement(self):
        """Import bank statement PDF and parse transactions."""
        # Update status
        self.import_status_label.config(text="Select a PDF bank statement...", fg="gray")

        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Bank Statement PDF",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            self.import_status_label.config(text="", fg="gray")
            return

        # Update status
        self.import_status_label.config(text="Parsing bank statement...", fg="blue")
        self.root.update()

        try:
            # Parse the statement
            result = self.statement_parser.parse_statement(file_path)

            if result['error']:
                self.import_status_label.config(
                    text=f"Error: {result['error']}",
                    fg="red"
                )
                messagebox.showerror("Parsing Error", result['error'])
                return

            # Store transactions for preview
            self.pending_transactions = result['transactions']

            # Clear preview tree
            for item in self.import_preview_tree.get_children():
                self.import_preview_tree.delete(item)

            # Add transactions to preview
            for trans in self.pending_transactions:
                amount_str = f"${trans['amount']:.2f}"
                if trans['type'] == 'expense':
                    amount_str = f"-{amount_str}"
                else:
                    amount_str = f"+{amount_str}"

                self.import_preview_tree.insert('', 'end', values=(
                    trans['date'],
                    trans['description'][:50],  # Truncate long descriptions
                    amount_str,
                    trans['type'].capitalize(),
                    trans['category']
                ))

            # Update status
            count = len(self.pending_transactions)
            account = result['account_number'] or 'Unknown'

            status_msg = f"✓ Found {count} transactions from account {account}"
            self.import_status_label.config(text=status_msg, fg="green")

            # Enable import button
            if count > 0:
                self.import_all_button.config(state='normal')

            # Show summary
            messagebox.showinfo(
                "Statement Parsed",
                f"Successfully parsed bank statement!\n\n"
                f"Account: {account}\n"
                f"Transactions found: {count}\n"
                f"Statement period: {result['statement_period']['start_date']} to "
                f"{result['statement_period']['end_date']}\n\n"
                f"Review the transactions in the preview and click 'Import All Transactions' to add them."
            )

        except Exception as e:
            self.import_status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Failed to parse statement: {str(e)}")

    def import_all_transactions(self):
        """Import all pending transactions to the database."""
        if not self.pending_transactions:
            messagebox.showwarning("Warning", "No transactions to import.")
            return

        # Confirm import
        count = len(self.pending_transactions)
        if not messagebox.askyesno(
            "Confirm Import",
            f"Import {count} transactions to the database?\n\n"
            f"This action cannot be undone."
        ):
            return

        try:
            imported = 0
            failed = 0

            for trans in self.pending_transactions:
                try:
                    self.db.add_transaction(
                        trans['date'],
                        trans['type'],
                        trans['category'],
                        trans['amount'],
                        trans['description']
                    )
                    imported += 1
                except Exception as e:
                    failed += 1
                    print(f"Failed to import transaction: {e}")

            # Clear pending transactions
            self.pending_transactions = []
            self.clear_import_preview()
            self.import_all_button.config(state='disabled')

            # Refresh transaction list and summary
            self.refresh_transaction_list()
            self.update_summary()

            # Show result
            if failed == 0:
                messagebox.showinfo(
                    "Import Complete",
                    f"Successfully imported {imported} transactions!"
                )
            else:
                messagebox.showwarning(
                    "Import Complete with Errors",
                    f"Imported: {imported} transactions\n"
                    f"Failed: {failed} transactions"
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import transactions: {str(e)}")

    def clear_import_preview(self):
        """Clear the import preview tree."""
        for item in self.import_preview_tree.get_children():
            self.import_preview_tree.delete(item)

        self.pending_transactions = []
        self.import_all_button.config(state='disabled')
        self.import_status_label.config(text="", fg="gray")


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = AccountingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
