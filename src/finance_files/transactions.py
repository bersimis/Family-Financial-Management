# Import tkinter for GUI creation
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

# Import project files
from database import database
from login_system import auth
from finance_files import categories

import config_and_styles as style


# ---------------------------------------------------------------------
# ADD TRANSACTION FUNCTIONS
# ---------------------------------------------------------------------

def add_transaction(
    user_id,
    transaction_type,
    category_name,
    amount,
    transaction_date,
    is_monthly
):
    con = database.connect()

    if con is None:
        return

    try:
        cur = con.cursor()

        # Define category id
        cur.execute("""
            SELECT id
            FROM categories
            WHERE name = ?
            AND type = ?
        """, (
            category_name,
            transaction_type.lower()
        ))

        category = cur.fetchone()

        if category is None:
            return

        category_id = category[0]

        # Insert transaction into database
        cur.execute("""
            INSERT INTO transactions
            (
                category_id,
                amount,
                date,
                is_monthly,
                created_by
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            category_id,
            amount,
            transaction_date,
            is_monthly,
            user_id
        ))

        con.commit()

    except Exception as error:
        print("Error adding transaction:", error)

    finally:
        con.close()


# ---------------------------------------------------------------------
# IINSERT GET TRANSACTIONS FUNCTIONS


def get_transactions():

    con = database.connect()

    if con is None:
        return []

    try:
        cur = con.cursor()
       
        cur.execute("""
             SELECT
                transactions.id,
                transactions.date,
                categories.type,
                categories.name,
                transactions.amount,
                transactions.is_monthly,
                COALESCE(users.username, 'Unknown') AS username
            FROM transactions

            INNER JOIN categories
            ON transactions.category_id = categories.id

            LEFT JOIN users
            ON transactions.created_by = users.id
                
            ORDER BY transactions.date DESC
        """)
        
        return cur.fetchall()

    except Exception as error:
        print("Error loading transactions:", error)
        return []

    finally:
        con.close()



# ---------------------------------------------------------------------
# DELETE TRANSACTIONS FUNCTIONS
# ---------------------------------------------------------------------
def delete_transaction(transaction_id):
    con = database.connect()

    if con is None:
        return

    try:
        cur = con.cursor()

        cur.execute("""
            DELETE FROM transactions
            WHERE id = ?
        """, (transaction_id,))

        con.commit()

    except Exception as error:
        print("Error deleting transaction:", error)

    finally:
        con.close()

#Object-oriented programming, definition of classes, inheritance
        
class TransactionsFrame:
    def __init__(self, parent):
        # Store parent frame
        self.parent = parent

        # Create main frame
        self.frame = tk.Frame(parent, bg=style.COLOR_BG_MAIN)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Build interface
        self.create_form()
        self.create_table()
        self.load_transactions()

    def get_current_user_id(self):
        # Get the currently logged-in user from auth.py.
        current_user = auth.get_user()

        # If a user is logged in, return the database id of this user.
        if current_user is not None:
            return current_user.id

        # Fallback id for testing without login.
        return 1

    def get_current_user_role_id(self):
        # Get the currently logged-in user from auth.py.
        current_user = auth.get_user()

        # If a user is logged in, return their role_id.
        # Expected roles: 1 = admin/parent, 2 = editor, 3 = viewer.
        if current_user is not None:
            return current_user.role_id

        # Safe fallback for testing: non-admin users can only see their own transactions.
        return None
    
    # Method

    def create_form(self):
        # Create title 
        title = tk.Label(
            self.frame,
            text="Add Income / Expense",
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, 20, "bold")
        )
        title.pack(pady=10)

        # Create form frame
        form = tk.Frame(self.frame, bg=style.COLOR_BG_MAIN)
        form.pack(pady=10)

        # Type label
        tk.Label(
            form,
            text="Type:",
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
        ).grid(row=0, column=0, padx=5, pady=5)

        # Transaction type variable
        self.type_var = tk.StringVar(value="expense")

        # Transaction type dropdown
        self.type_combo = ttk.Combobox(
            form,
            textvariable=self.type_var,
            values=["income", "expense"],
            state="readonly",
            width=18,
            font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT)
        )
        self.type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.type_combo.bind("<<ComboboxSelected>>", lambda event: self.load_categories())

        # Category label
        tk.Label(
            form,
            text="Category:",
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Category dropdown
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            form,
            textvariable=self.category_var,
            state="readonly",
            width=18,
            font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT)
        )
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        #Create + button
        tk.Button(
            form,
            text="Add category",
            width=12,
            bg=style.COLOR_PRIMARY,
            fg=style.COLOR_LIGHT,
            font=(style.FONT_FAMILY, 10,"bold"),
            command=self.open_categories_window
            ).grid(row=1, column=3, padx=5, pady=5)
       

        # Amount label
        tk.Label(
            form,
            text="Amount:",
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
        ).grid(row=2, column=0, padx=5, pady=5)

        # Amount input
        self.amount_entry = tk.Entry(
            form,
            width=21,
            font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN
        )
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        # Date label
        tk.Label(
            form,
            text="Date:",
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
        ).grid(row=2, column=2, padx=5, pady=5)

        # Date input
        self.date_entry = tk.Entry(
            form,
            width=21,
            font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN
        )
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=2, column=3, padx=5, pady=5)

        # Monthly checkbox variable
        self.monthly_var = tk.IntVar(value=0)

        # Monthly checkbox
        self.monthly_check = tk.Checkbutton(
            form,
            text="Monthly transaction",
            variable=self.monthly_var,
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
        )
        self.monthly_check.grid(row=3, column=1, padx=5, pady=5)

        #Insert Auto transaction day Label]
        tk.Label(
            form,
            text="Auto Transaction Day:",
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
            ).grid(row=3, column=2, padx=5, pady=5)

        #Input of auto transaction day
        self.auto_transaction_day_entry=tk.Entry(
            form,
            width=21,
            font=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN
        )

        self.auto_transaction_day_entry.grid(
            row=3,
            column=3,
            padx=5,
            pady=5
        )


        # Save button
        tk.Button(
            form,
            text="Save Transaction",
            command=self.save_transaction,
            bg=style.COLOR_SUCCESS,
            fg=style.COLOR_LIGHT,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON, "bold"),
            width=20
        ).grid(row=4, column=1, pady=15)

        # Delete button
        tk.Button(
            form,
            text="Delete Selected",
            command=self.delete_selected_transaction,
            bg=style.COLOR_DANGER,
            fg=style.COLOR_LIGHT,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON, "bold"),
            width=20
        ).grid(row=4, column=2, pady=15)

        # Load categories into dropdown
        self.load_categories()
        
        
    def create_table(self):
        # Define table columns
        columns = ("id", "date", "type", "category", "amount", "monthly", "user")

        # Create table
        self.tree = ttk.Treeview(
            self.frame,
            columns=columns,
            show="headings",
            height=13
        )

        # Table headings
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("type", text="Type")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("monthly", text="Monthly")
        self.tree.heading("user", text="User")

        # Column sizes
        self.tree.column("id", width=50)
        self.tree.column("date", width=120)
        self.tree.column("type", width=100)
        self.tree.column("category", width=160)
        self.tree.column("amount", width=120)
        self.tree.column("monthly", width=100)
        self.tree.column("user", width=140)

        # Place table
        self.tree.pack(expand=True, fill="both", pady=10)

    def load_categories(self):
        try:
            # Get user id from auth.py
            user_id = self.get_current_user_id()

            # Get selected transaction type
            transaction_type = self.type_var.get()

            # Get categories
            category_list = categories.get_categories(user_id, transaction_type)

            # Extract category names
            category_names = [category[1] for category in category_list]

            # Add names to dropdown
            self.category_combo["values"] = category_names

            # Select first category if exists
            if category_names:
                self.category_var.set(category_names[0])
            else:
                self.category_var.set("")

        except Exception as error:
            messagebox.showerror("Error", f"Could not load categories:\n{error}")

    def save_transaction(self):
        try:
            # Get user id
            user_id = self.get_current_user_id()

            # Get values from form
            transaction_type = self.type_var.get()
            category = self.category_var.get()
            amount_text = self.amount_entry.get().strip()
            transaction_date = self.date_entry.get().strip()
            is_monthly = self.monthly_var.get()

            # Validate category
            if not category:
                messagebox.showwarning("Validation Error", "Please select a category.")
                return

            # Validate amount
            if not amount_text:
                messagebox.showwarning("Validation Error", "Please enter an amount.")
                return

            # Convert amount to number
            amount = float(amount_text)

            # Check positive amount
            if amount <= 0:
                messagebox.showwarning("Validation Error", "Amount must be greater than zero.")
                return

            # Save transaction
            add_transaction(
                user_id,
                transaction_type,
                category,
                amount,
                transaction_date,
                is_monthly
            )

            # Success message
            messagebox.showinfo("Success", "Transaction saved successfully.")

            # Clear input fields
            self.amount_entry.delete(0, tk.END)
            self.monthly_var.set(0)

            # Refresh table
            self.load_transactions()

        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number.")

        except Exception as error:
            messagebox.showerror("Error", f"Could not save transaction:\n{error}")


    def load_transactions(self):
        try:
            # Clear table
            for row in self.tree.get_children():
                self.tree.delete(row)

          # Get current logged-in user
            current_user = auth.get_user()

          # Load transactions depending on role
            transactions = get_transactions()
               

         # Insert transactions into table
            for transaction in transactions:
                print(transaction)
                self.tree.insert("", tk.END, values=transaction)

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Could not load transactions:\n{error}"
            )


  
    #Parent definition
    def open_categories_window(self):
        categories.CategoriesWindow(self.frame)

    def delete_selected_transaction(self):
        # Get selected row
        selected_item = self.tree.selection()

        # Check selection
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a transaction to delete.")
            return

        # Confirm delete
        answer = messagebox.askyesno(
            "Delete Transaction",
            "Are you sure you want to delete this transaction?"
        )

        if not answer:
            return

        try:
            # Get transaction id
            item_values = self.tree.item(selected_item)["values"]
            transaction_id = item_values[0]

            # Delete transaction
            delete_transaction(transaction_id)

            # Success message
            messagebox.showinfo("Success", "Transaction deleted successfully.")

            # Refresh table
            self.load_transactions()

        except Exception as error:
            messagebox.showerror("Error", f"Could not delete transaction:\n{error}")
