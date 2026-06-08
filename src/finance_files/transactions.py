# Import tkinter for GUI creation
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import logging
# Import project files
from database import database
from login_system import auth
from finance_files import categories
import config_and_styles as style


# ---------------------------------------------------------------------
# FILTER ADDITIONS TO ASSIST FUNCTIONS
# ---------------------------------------------------------------------
def get_all_categories():
    con = database.connect()
    if con is None:
        return []
    try:
        cur = con.cursor()
        cur.execute("SELECT DISTINCT name FROM categories ORDER BY name ASC")
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        logging.exception("Error getting all categories from database.")
        print("Error getting all categories:", e)
        return []
    finally:
        con.close()

def get_all_users():
    con = database.connect()
    if con is None:
        return []
    try:
        cur = con.cursor()
        cur.execute("SELECT DISTINCT username FROM users ORDER BY username ASC")
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        logging.exception("Error getting all users from database.")
        print("Error getting all users:", e)
        return []
    finally:
        con.close()


    
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
        logging.exception("Error adding transaction to database.")
        print("Error adding transaction:", error)

    finally:
        con.close()


# ---------------------------------------------------------------------
# GET TRANSACTIONS FUNCTIONS
# ---------------------------------------------------------------------
def get_transactions(category_filter=None, user_filter=None):
    con = database.connect()

    if con is None:
        return []

    try:
        cur = con.cursor()
       
        # Base query to fetch transactions along with category details and author username
        query = """
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
            
            WHERE 1=1
        """
        params = []

        # Filter by Category name
        if category_filter and category_filter != "All":
            query += " AND categories.name = ?"
            params.append(category_filter)

        # Filter by User's username
        if user_filter and user_filter != "All":
            query += " AND users.username = ?"
            params.append(user_filter)

        # Default sorting by Date DESC
        query += " ORDER BY transactions.date DESC"

        cur.execute(query, tuple(params))
        return cur.fetchall()

    except Exception as error:
        logging.exception("Error loading transactions from database.")
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
        logging.exception("Error deleting transaction from database.")
        print("Error deleting transaction:", error)

    finally:
        con.close()

#---------------------------------------------------------------------
#GENERATING MONTHLY RECURRING TRANSACTIONS SYSTEM
#---------------------------------------------------------------------
def check_and_generate_recurring_transactions():
    #This function scans the database for recurring templates (is_monthly = 1)
    #and automatically generates any missing monthly transactions up to today.
    con = database.connect()
    if con is None:
        return
    try:
        cur = con.cursor()
        
        #Get all transactions marked as monthly templates
        cur.execute("""
            SELECT id, category_id, amount, date, created_by
            FROM transactions
            WHERE is_monthly = 1
        """)
        templates = cur.fetchall()
        
        from datetime import datetime, date, timedelta
        today = date.today()
        
        for template_id, category_id, amount, start_date_str, created_by in templates:
            try:
                #Parse start date of the template
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue
                
            #Loop through each subsequent month up to today
            current_month_date = start_date
            
            while True:
                #Calculate the next month's year and month
                if current_month_date.month == 12:
                    next_year = current_month_date.year + 1
                    next_month = 1
                else:
                    next_year = current_month_date.year
                    next_month = current_month_date.month + 1
                    
                #We keep the same day (auto transaction day)
                day = start_date.day
                
                #Handle months with fewer days (e.g. 31st of February becomes 28th/29th)
                while True:
                    try:
                        next_date = date(next_year, next_month, day)
                        break
                    except ValueError:
                        day -= 1
                        if day < 1:
                            break
                
                #If next_date is in the future relative to today, stop generating for this template
                if next_date > today:
                    break
                    
                #Check if a transaction already exists for this template in next month
                #We look for same category_id, same amount, same user, and same month/year
                start_of_month = next_date.replace(day=1).strftime("%Y-%m-%d")
                
                if next_month == 12:
                    end_of_month = date(next_year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_of_month = date(next_year, next_month + 1, 1) - timedelta(days=1)
                end_of_month_str = end_of_month.strftime("%Y-%m-%d")
                
                cur.execute("""
                    SELECT id FROM transactions
                    WHERE category_id = ?
                    AND amount = ?
                    AND created_by = ?
                    AND date >= ?
                    AND date <= ?
                """, (category_id, amount, created_by, start_of_month, end_of_month_str))
                
                if cur.fetchone() is None:
                    #Create the recurring transaction for this month
                    cur.execute("""
                        INSERT INTO transactions (category_id, amount, date, is_monthly, created_by)
                        VALUES (?, ?, ?, ?, ?)
                    """, (category_id, amount, next_date.strftime("%Y-%m-%d"), 1, created_by))
                    
                current_month_date = next_date
                
        con.commit()
    except Exception as e:
        logging.exception("Error processing recurring transactions.")
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
        role_id = self.get_current_user_role_id()
        if role_id != 3:
            self.create_form()
        else:
            #ShowSimpleTitleForViewer
            title = tk.Label(
                self.frame,
                text="Transactions Table",
                bg=style.COLOR_BG_MAIN,
                fg=style.COLOR_TEXT_MAIN,
                font=(style.FONT_FAMILY, 20, "bold")
            )
            title.pack(pady=10)
            
        self.create_filter_bar()
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
        self.auto_transaction_day_entry = tk.Spinbox(
            form,
            from_=1,
            to=31,
            width=19,
            state="readonly",
            font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
            bg=style.COLOR_BG_CARD,
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
            logging.exception("Could not load categories in UI.")
            messagebox.showerror("Error", f"Could not load categories:\n{error}")

    def save_transaction(self):
        try:
            #Prevent viewers from modifying data
            role_id = self.get_current_user_role_id()
            if role_id == 3:
                messagebox.showwarning("Permission Error", "Viewers are not allowed to make changes.")
                return

            # Get user id
            user_id = self.get_current_user_id()

            # Get values from form
            transaction_type = self.type_var.get()
            category = self.category_var.get()
            amount_text = self.amount_entry.get().strip()
            transaction_date = self.date_entry.get().strip()
            is_monthly = self.monthly_var.get()

            #Adding validation error function
            if is_monthly == 1:
                try:
                    auto_transcaction_day = self.auto_transaction_day_entry.get().strip()
                    auto_transaction_day = int(auto_transcaction_day)
                    if auto_transaction_day < 1 or auto_transaction_day > 31:
                        messagebox.showwarning(
                            "Validation Error",
                            "Auto Transaction Day must be between 1 and 31."
                        )
                        return
                    
                    #Adjust day of transaction_date to selected auto_transaction_day
                    parts = transaction_date.split("-")
                    if len(parts) == 3:
                        yr, mn = int(parts[0]), int(parts[1])
                        dy = auto_transaction_day
                        #Handle month day limits
                        while True:
                            try:
                                from datetime import date as dt_date
                                test_date = dt_date(yr, mn, dy)
                                transaction_date = test_date.strftime("%Y-%m-%d")
                                break
                            except ValueError:
                                dy -= 1
                                if dy < 1:
                                    break
                except ValueError:
                    messagebox.showwarning(
                        "Validation Error",
                        "Auto Transaction Day must be a number."
                    )
                    return

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
            logging.exception("Could not save transaction in UI.")
            messagebox.showerror("Error", f"Could not save transaction:\n{error}")


    def load_transactions(self):
        try:
            #Run automatic monthly transaction generator first
            check_and_generate_recurring_transactions()

            # Clear table
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Get filter values safely using default fallback if filter widgets are not initialized yet
            category_filter = self.filter_category_var.get() if hasattr(self, 'filter_category_var') else "All"
            user_filter = self.filter_user_var.get() if hasattr(self, 'filter_user_var') else "All"

            # Load filtered transactions from database
            transactions = get_transactions(
                category_filter=category_filter,
                user_filter=user_filter
            )

            # Insert transactions into table
            for transaction in transactions:
                self.tree.insert("", tk.END, values=transaction)

        except Exception as error:
            logging.exception("Could not load transactions in UI.")
            messagebox.showerror(
                "Error",
                f"Could not load transactions:\n{error}"
            )

    def create_filter_bar(self):
        # Create a horizontal frame for the filter controls (card look)
        self.filter_frame = tk.LabelFrame(
            self.frame,
            text="Filter Transactions",
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, 10, "bold"),
            padx=15,
            pady=10
        )
        self.filter_frame.pack(fill="x", pady=10)

        # 1. Category Filter
        tk.Label(
            self.filter_frame,
            text="Category:",
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
        ).pack(side="left", padx=(10, 5))

        self.filter_category_var = tk.StringVar(value="All")
        self.filter_category_combo = ttk.Combobox(
            self.filter_frame,
            textvariable=self.filter_category_var,
            state="readonly",
            width=15,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
        )
        self.filter_category_combo.pack(side="left", padx=5)
        self.filter_category_combo.bind("<<ComboboxSelected>>", lambda event: self.load_transactions())

        # 2. User Filter
        tk.Label(
            self.filter_frame,
            text="User:",
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
        ).pack(side="left", padx=(20, 5))

        self.filter_user_var = tk.StringVar(value="All")
        self.filter_user_combo = ttk.Combobox(
            self.filter_frame,
            textvariable=self.filter_user_var,
            state="readonly",
            width=15,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
        )
        self.filter_user_combo.pack(side="left", padx=5)
        self.filter_user_combo.bind("<<ComboboxSelected>>", lambda event: self.load_transactions())

        # Buttons (Apply & Clear)
        tk.Button(
            self.filter_frame,
            text="Clear Filters",
            command=self.clear_filters,
            bg=style.COLOR_DANGER,
            fg=style.COLOR_LIGHT,
            font=(style.FONT_FAMILY, 10, "bold"),
            width=12
        ).pack(side="right", padx=10)

        tk.Button(
            self.filter_frame,
            text="Apply Filters",
            command=self.load_transactions,
            bg=style.COLOR_PRIMARY,
            fg=style.COLOR_LIGHT,
            font=(style.FONT_FAMILY, 10, "bold"),
            width=12
        ).pack(side="right", padx=10)

        # Load filter options dynamically
        self.populate_filter_combos()

    def populate_filter_combos(self):
        try:
            # Populates categories combo
            cats = get_all_categories()
            self.filter_category_combo["values"] = ["All"] + cats

            # Populates users combo
            users = get_all_users()
            self.filter_user_combo["values"] = ["All"] + users

        except Exception as error:
            logging.exception("Error populating filter combos in UI.")
            print("Error populating filter combos:", error)

    def clear_filters(self):
        self.filter_category_var.set("All")
        self.filter_user_var.set("All")
        self.load_transactions()


  
    #Parent definition
    def open_categories_window(self):
        categories.CategoriesWindow(self.frame)

    def delete_selected_transaction(self):
        #Prevent viewers from deleting data
        role_id = self.get_current_user_role_id()
        if role_id == 3:
            messagebox.showwarning("Permission Error", "Viewers are not allowed to make changes.")
            return

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
            logging.exception("Could not delete selected transaction in UI.")
            messagebox.showerror("Error", f"Could not delete transaction:\n{error}")
