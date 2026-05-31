# Import tkinter library for GUI creation
import tkinter as tk
import logging

# Import ttk for advanced widgets and messagebox for popup messages
from tkinter import ttk, messagebox

# Import database file to communicate with SQLite database
from database import database

# Import auth file from login_system
from login_system import auth

# Import configuration and style constants
import config_and_styles as style


# ---------------------------------------------------------------------
# GET CATEGORIES
# ---------------------------------------------------------------------
def get_categories(user_id, category_type):
    con = database.connect()

    if con is None:
        return []

    try:
        cur = con.cursor()

        cur.execute("""
            SELECT id, name, type
            FROM categories
            WHERE type = ?
            ORDER BY name
        """, (category_type.lower(),))

        return cur.fetchall()

    except Exception as error:
        logging.exception("Error loading categories from database.")
        print("Error loading categories:", error)
        return []

    finally:
        con.close()


# ---------------------------------------------------------------------
# ADD CATEGORY
# ---------------------------------------------------------------------
def add_category(user_id, category_name, category_type):
    con = database.connect()

    if con is None:
        return

    try:
        cur = con.cursor()

        cur.execute("""
            INSERT INTO categories (name, type)
            VALUES (?, ?)
        """, (category_name, category_type.lower()))

        con.commit()

    except Exception as error:
        logging.exception("Error adding category to database.")
        print("Error adding category:", error)

    finally:
        con.close()


# ---------------------------------------------------------------------
# DELETE CATEGORY
# ---------------------------------------------------------------------
def delete_category(category_id):
    con = database.connect()

    if con is None:
        return

    try:
        cur = con.cursor()

        cur.execute("""
            DELETE FROM categories
            WHERE id = ?
        """, (category_id,))

        con.commit()

    except Exception as error:
        logging.exception("Error deleting category from database.")
        print("Error deleting category:", error)

    finally:
        con.close()


class CategoriesWindow:

    def __init__(self, parent):
        # Create a new top-level window
        self.window = tk.Toplevel(parent)

        # Set window title
        self.window.title("Manage Categories")

        # Set window size
        self.window.geometry("500x450")

        # Disable resize option
        self.window.resizable(False, False)

        # Apply background color from config_and_styles.py
        self.window.configure(bg=style.COLOR_BG_MAIN)

        # Create all GUI widgets
        self.create_widgets()

        # Load categories from database
        self.load_categories()

    def get_current_user_id(self):
        # Get the current logged-in user from auth.py
        current_user = auth.get_user()

        # If no user is logged in, use admin user id for testing
        if current_user is not None:
            return current_user.id

        return 1

    def create_widgets(self):
        # Create title label
        title = tk.Label(
            self.window,
            text="Category Management",
            font=(style.FONT_FAMILY, 20, "bold"),
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN
        )
        title.pack(pady=15)

        # Create form frame
        form = tk.Frame(
            self.window,
            bg=style.COLOR_BG_MAIN
        )
        form.pack(pady=10)

        # Create label for category type
        tk.Label(
            form,
            text="Type:",
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT),
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN
        ).grid(row=0, column=0, padx=5, pady=5)

        # Store selected category type
        self.type_var = tk.StringVar(value="expense")

        # Create combobox for category type
        self.type_combo = ttk.Combobox(
            form,
            textvariable=self.type_var,
            values=["income", "expense"],
            state="readonly",
            width=18,
            font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT)
        )
        self.type_combo.grid(row=0, column=1, padx=5, pady=5)

        # Reload categories when type changes
        self.type_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self.load_categories()
        )

        # Create label for category name
        tk.Label(
            form,
            text="Category name:",
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT),
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN
        ).grid(row=1, column=0, padx=5, pady=5)

        # Create input field for category name
        self.name_entry = tk.Entry(
            form,
            width=21,
            font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN,
            relief="solid",
            bd=1
        )
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        # Create button for adding category
        tk.Button(
            form,
            text="Add Category",
            command=self.add_category,
            bg=style.COLOR_SUCCESS,
            fg=style.COLOR_LIGHT,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON, "bold"),
            width=18,
            relief="flat"
        ).grid(row=2, column=0, pady=10, padx=5)

        # Create button for deleting category
        tk.Button(
            form,
            text="Delete Selected",
            command=self.delete_category,
            bg=style.COLOR_DANGER,
            fg=style.COLOR_LIGHT,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON, "bold"),
            width=18,
            relief="flat"
        ).grid(row=2, column=1, pady=10, padx=5)

        # Define table columns
        columns = ("id", "name", "type")

        # Create Treeview table
        self.tree = ttk.Treeview(
            self.window,
            columns=columns,
            show="headings",
            height=12
        )

        # Create table headings
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("type", text="Type")

        # Set table column widths
        self.tree.column("id", width=50)
        self.tree.column("name", width=220)
        self.tree.column("type", width=120)

        # Place table on window
        self.tree.pack(pady=15)

    def load_categories(self):
        try:
            # Clear old rows from table
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Get current user id from auth.py
            user_id = self.get_current_user_id()

            # Get selected category type
            category_type = self.type_var.get()

            # Retrieve categories
            categories = get_categories(user_id, category_type)

            # Insert categories into table
            for category in categories:
                self.tree.insert("", tk.END, values=category)

        except Exception as error:
            logging.exception("Could not load categories in UI.")
            messagebox.showerror(
                "Error",
                f"Could not load categories:\n{error}"
            )

    def add_category(self):
        try:
            # Get current user id from auth.py
            user_id = self.get_current_user_id()

            # Get category name from input field
            category_name = self.name_entry.get().strip()

            # Get selected category type
            category_type = self.type_var.get()

            # Check if category name is empty
            if not category_name:
                messagebox.showwarning(
                    "Validation Error",
                    "Please enter a category name."
                )
                return

            # Add category
            add_category(user_id, category_name, category_type)

            # Show success message
            messagebox.showinfo(
                "Success",
                "Category added successfully."
            )

            # Clear input field
            self.name_entry.delete(0, tk.END)

            # Reload table
            self.load_categories()

        except Exception as error:
            logging.exception("Could not add category in UI.")
            messagebox.showerror(
                "Error",
                f"Could not add category:\n{error}"
            )

    def delete_category(self):
        # Get selected row
        selected_item = self.tree.selection()

        # Check if user selected a category
        if not selected_item:
            messagebox.showwarning(
                "Selection Error",
                "Please select a category to delete."
            )
            return

        # Ask for confirmation
        answer = messagebox.askyesno(
            "Delete Category",
            "Are you sure you want to delete this category?"
        )

        # Stop if user clicks No
        if not answer:
            return

        try:
            # Get selected row values
            item_values = self.tree.item(selected_item)["values"]

            # Get category id from selected row
            category_id = item_values[0]

            # Delete category
            delete_category(category_id)

            # Show success message
            messagebox.showinfo(
                "Success",
                "Category deleted successfully."
            )

            # Reload table
            self.load_categories()

        except Exception as error:
            logging.exception("Could not delete category in UI.")
            messagebox.showerror(
                "Error",
                f"Could not delete category:\n{error}"
            )
