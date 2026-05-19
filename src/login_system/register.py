# Register.py
# This py file handles the registration of a new user.

import sqlite3
import logging
import string
import datetime
import hashlib
import tkinter as tk

from database import database
from login_system import auth


# -------------------------------------------------------------------------
# Validate username: must only contain letters and digits.
def check_username(user_input, error_lbl=None):
    valid_username = string.ascii_letters + string.digits
    if not user_input:
        if error_lbl:
            error_lbl.config(text="Username cannot be empty")
        return False

    for char in user_input:
        if char not in valid_username:
            if error_lbl:
                error_lbl.config(text="Username must be letters and numbers only")
            return False
    return True


# -------------------------------------------------------------------------
# Validate password: must be at least 8 characters long and contain safe chars.
def check_password(password_input, error_lbl=None):
    if len(password_input) < 8:
        if error_lbl:
            error_lbl.config(text="Password must be at least 8 characters long")
        return False

    valid_password = string.ascii_letters + string.digits + "!@#$%"
    for char in password_input:
        if char not in valid_password:
            if error_lbl:
                error_lbl.config(text="Password must only contain a-z, A-Z, 0-9, or !@#$%")
            return False
    return True


# -------------------------------------------------------------------------
# Validate password confirmation: must match password and not be empty.
def check_confirm_password(confirm_password_input, password_input, error_lbl=None):
    if not confirm_password_input:
        if error_lbl:
            error_lbl.config(text="Please confirm your password")
        return False
    if confirm_password_input != password_input:
        if error_lbl:
            error_lbl.config(text="Passwords do not match")
        return False
    return True


# -------------------------------------------------------------------------
# Validate birth year: must be between 1900 and this_year - 1.
def check_birthyear(birth_year_input, error_lbl=None):
    try:
        year = int(birth_year_input)
    except ValueError:
        if error_lbl:
            error_lbl.config(text="Birth year must be a valid number")
        return False

    this_year = datetime.datetime.now().year
    if year >= 1900 and year <= this_year - 1:
        return True
    else:
        if error_lbl:
            error_lbl.config(text=f"Birth year must be between 1900 and {this_year - 1}")
        return False


# -------------------------------------------------------------------------
# Processes the registration on button click.
def start_register(username_entry, password_entry, confirm_password_entry, birthyear_entry, error_lbl, root):
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    confirm_password = confirm_password_entry.get().strip()
    birthyear_str = birthyear_entry.get().strip()

    # Clear previous error messages.
    error_lbl.config(text="")

    # Verify fields are not empty.
    if not username or not password or not confirm_password or not birthyear_str:
        error_lbl.config(text="Please fill in all fields")
        return

    # Run check validations.
    if not check_username(username, error_lbl):
        return
    if not check_password(password, error_lbl):
        return
    if not check_confirm_password(confirm_password, password, error_lbl):
        return
    if not check_birthyear(birthyear_str, error_lbl):
        return

    birth_year = int(birthyear_str)
    con = database.connect()
    if con is None:
        error_lbl.config(text="Could not connect to database")
        return

    try:
        cur = con.cursor()

        # Check if username already exists.
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone() is not None:
            error_lbl.config(text="Username already exists")
            return

        # Hash the password for security.
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Calculate user age.
        this_year = datetime.datetime.now().year
        age = this_year - birth_year
        role_id = 3  # All new users are registered as 'viewer' (id = 3).

        # Insert user into database.
        cur.execute("""
            INSERT INTO users (username, password, birth_year, age, role_id)
            VALUES (?, ?, ?, ?, ?)
        """, (username, hashed_password, birth_year, age, role_id))
        con.commit()

        # Alert user of success and redirect to login screen.
        from tkinter import messagebox
        messagebox.showinfo("Success", "Account created successfully! You can now log in.")

        from login_system import login
        login.build_login_gui(root)

    except Exception as e:
        logging.exception("An error occurred during registration.")
        error_lbl.config(text="An error occurred. Please try again.")
    finally:
        con.close()


# -------------------------------------------------------------------------
# Build the registration UI view.
def build_register_gui(root):
    from login_system import login
    import config_and_styles as style

    # Set background color for main window.
    root.configure(bg=style.COLOR_BG_MAIN)

    # Clear existing widgets from root window.
    for widget in root.winfo_children():
        widget.destroy()

    # Register Window Title.
    label = tk.Label(
        root,
        text="Register",
        font=(style.FONT_FAMILY, style.FONT_SIZE_TITLE, "bold"),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_TEXT_MAIN
    )
    label.pack(pady=40)

    # Form field container.
    form_frame = tk.Frame(root, bg=style.COLOR_BG_MAIN)
    form_frame.pack(pady=10)

    # Username Label & Input.
    tk.Label(
        form_frame,
        text="Username:",
        font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_TEXT_MAIN
    ).grid(row=0, column=0, sticky="e", padx=5, pady=10)

    username_entry = tk.Entry(
        form_frame,
        font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
        relief="solid",
        bd=1
    )
    username_entry.grid(row=0, column=1, padx=5, pady=10)

    # Password Label & Input.
    tk.Label(
        form_frame,
        text="Password:",
        font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_TEXT_MAIN
    ).grid(row=1, column=0, sticky="e", padx=5, pady=10)

    password_entry = tk.Entry(
        form_frame,
        font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
        show="*",
        relief="solid",
        bd=1
    )
    password_entry.grid(row=1, column=1, padx=5, pady=10)

    # Confirm Password Label & Input.
    tk.Label(
        form_frame,
        text="Confirm Password:",
        font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_TEXT_MAIN
    ).grid(row=2, column=0, sticky="e", padx=5, pady=10)

    confirm_password_entry = tk.Entry(
        form_frame,
        font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
        show="*",
        relief="solid",
        bd=1
    )
    confirm_password_entry.grid(row=2, column=1, padx=5, pady=10)

    # Birth Year Label & Input.
    tk.Label(
        form_frame,
        text="Birth Year:",
        font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_TEXT_MAIN
    ).grid(row=3, column=0, sticky="e", padx=5, pady=10)

    birthyear_entry = tk.Entry(
        form_frame,
        font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
        relief="solid",
        bd=1
    )
    birthyear_entry.grid(row=3, column=1, padx=5, pady=10)

    # Error Feedback Label.
    error_lbl = tk.Label(
        root,
        text="",
        font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_ERROR
    )
    error_lbl.pack(pady=5)

    # Register Submission Button.
    btn_register = tk.Button(
        root,
        text="REGISTER",
        font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON, "bold"),
        bg=style.COLOR_SUCCESS,
        fg=style.COLOR_LIGHT,
        width=15,
        command=lambda: start_register(username_entry, password_entry, confirm_password_entry, birthyear_entry, error_lbl, root)
    )
    btn_register.pack(pady=20)

    # Redirect to Login screen link.
    login_link = tk.Label(
        root,
        text="Already have an account? Log in here",
        font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT, "underline"),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_PRIMARY,
        cursor="hand2"
    )
    login_link.pack(pady=10)
    login_link.bind("<Button-1>", lambda event: login.build_login_gui(root))
    login_link.bind("<Enter>", lambda event: login_link.config(fg=style.COLOR_LINK_HOVER))
    login_link.bind("<Leave>", lambda event: login_link.config(fg=style.COLOR_PRIMARY))
