#Profile.py
#This file handles the user profile screen where users can update their username or password.

import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import string
import logging
from database import database
from login_system import auth
import config_and_styles as style

#-------------------------------------------------------------------------
#Validate username: must only contain letters and digits.
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

#-------------------------------------------------------------------------
#Validate password: must be at least 8 characters long and contain safe chars.
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

#-------------------------------------------------------------------------
#Validate password confirmation: must match password and not be empty.
def check_confirm_password(confirm_password_input, password_input, error_lbl=None):
    if not confirm_password_input:
        if error_lbl:
            error_lbl.config(text="Please confirm your new password")
        return False
    if confirm_password_input != password_input:
        if error_lbl:
            error_lbl.config(text="New passwords do not match")
        return False
    return True


class ProfileFrame:
    def __init__(self, dashboard, parent):
        #Store parent dashboard instance for live GUI updates (like sidebar username)
        self.dashboard = dashboard
        self.parent = parent

        #Create main container frame inside dashboard main area
        self.frame = tk.Frame(parent, bg=style.COLOR_BG_MAIN)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        #Construct the widgets of the view sequentially
        self.create_widgets()

    def create_widgets(self):
        #Display standard title at top of profile frame
        title = tk.Label(
            self.frame,
            text="MY PROFILE",
            font=(style.FONT_FAMILY, 24, "bold"),
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN
        )
        title.pack(pady=15)

        #Fetch the logged-in session user dynamically
        active_user = auth.get_user()
        username = active_user.username if active_user else "Guest"

        #-----------------------------------------------------------------
        #Card 1: Change Username Frame
        self.username_card = tk.LabelFrame(
            self.frame,
            text="Change Username",
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON, "bold"),
            padx=15,
            pady=15
        )
        self.username_card.pack(fill="x", pady=10)

        #Show current active username for clarity
        self.lbl_curr_user = tk.Label(
            self.username_card,
            text=f"Current Username: {username}",
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT, "bold"),
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MUTED
        )
        self.lbl_curr_user.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        #Input field for new username entry
        tk.Label(
            self.username_card,
            text="New Username:",
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT),
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)

        self.username_entry = tk.Entry(
            self.username_card,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT),
            width=25,
            relief="solid",
            bd=1
        )
        self.username_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        #Show validation error messages directly inside card below input
        self.username_error_lbl = tk.Label(
            self.username_card,
            text="",
            font=(style.FONT_FAMILY, 10),
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_ERROR
        )
        self.username_error_lbl.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        #Trigger button for username database updates
        self.btn_update_username = tk.Button(
            self.username_card,
            text="Update Username",
            font=(style.FONT_FAMILY, 11, "bold"),
            bg=style.COLOR_PRIMARY,
            fg=style.COLOR_LIGHT,
            command=self.update_username,
            width=18
        )
        self.btn_update_username.grid(row=3, column=1, sticky="w", padx=5, pady=5)


        #-----------------------------------------------------------------
        #Card 2: Change Password Frame
        self.password_card = tk.LabelFrame(
            self.frame,
            text="Change Password",
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON, "bold"),
            padx=15,
            pady=15
        )
        self.password_card.pack(fill="x", pady=15)

        #Old password field input for security verification
        tk.Label(
            self.password_card,
            text="Old Password:",
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT),
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN
        ).grid(row=0, column=0, sticky="e", padx=5, pady=8)

        self.old_password_entry = tk.Entry(
            self.password_card,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT),
            width=25,
            show="*",
            relief="solid",
            bd=1
        )
        self.old_password_entry.grid(row=0, column=1, padx=5, pady=8, sticky="w")

        #New password entry input field
        tk.Label(
            self.password_card,
            text="New Password:",
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT),
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN
        ).grid(row=1, column=0, sticky="e", padx=5, pady=8)

        self.new_password_entry = tk.Entry(
            self.password_card,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT),
            width=25,
            show="*",
            relief="solid",
            bd=1
        )
        self.new_password_entry.grid(row=1, column=1, padx=5, pady=8, sticky="w")

        #Confirm entry to prevent typos in new password
        tk.Label(
            self.password_card,
            text="Confirm Password:",
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT),
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN
        ).grid(row=2, column=0, sticky="e", padx=5, pady=8)

        self.confirm_password_entry = tk.Entry(
            self.password_card,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT),
            width=25,
            show="*",
            relief="solid",
            bd=1
        )
        self.confirm_password_entry.grid(row=2, column=1, padx=5, pady=8, sticky="w")

        #Show validation errors inside card
        self.password_error_lbl = tk.Label(
            self.password_card,
            text="",
            font=(style.FONT_FAMILY, 10),
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_ERROR
        )
        self.password_error_lbl.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        #Trigger button for password updates
        self.btn_update_password = tk.Button(
            self.password_card,
            text="Update Password",
            font=(style.FONT_FAMILY, 11, "bold"),
            bg=style.COLOR_SUCCESS,
            fg=style.COLOR_LIGHT,
            command=self.update_password,
            width=18
        )
        self.btn_update_password.grid(row=4, column=1, sticky="w", padx=5, pady=5)

    def update_username(self):
        new_username = self.username_entry.get().strip()
        self.username_error_lbl.config(text="")

        #Make sure input is not blank
        if not new_username:
            self.username_error_lbl.config(text="Please enter a new username")
            return

        #Ensure input contains safe valid alphanumeric characters
        if not check_username(new_username, self.username_error_lbl):
            return

        active_user = auth.get_user()
        if not active_user:
            self.username_error_lbl.config(text="Session expired. Please log in again.")
            return

        con = database.connect()
        if con is None:
            self.username_error_lbl.config(text="Could not connect to database")
            return

        try:
            cur = con.cursor()

            #Check database to make sure username is not already taken by another profile
            cur.execute("SELECT id FROM users WHERE username = ? AND id != ?", (new_username, active_user.id))
            if cur.fetchone() is not None:
                self.username_error_lbl.config(text="Username already exists")
                return

            #Execute SQL UPDATE statement to modify username in table
            cur.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, active_user.id))
            con.commit()

            #Update session information so other sections read the modified username
            active_user.username = new_username
            
            #Live sync: update current display labels in dashboard sidebar and profile frame immediately
            self.lbl_curr_user.config(text=f"Current Username: {new_username}")
            self.dashboard.user_label.config(text=f"User: {new_username}")
            
            #Reset entry field value
            self.username_entry.delete(0, tk.END)

            messagebox.showinfo("Success", "Username updated successfully!")

        except Exception as e:
            logging.exception("Error updating username")
            self.username_error_lbl.config(text="Error updating username")
        finally:
            con.close()

    def update_password(self):
        old_password = self.old_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        self.password_error_lbl.config(text="")

        #Ensure all fields are filled
        if not old_password or not new_password or not confirm_password:
            self.password_error_lbl.config(text="Please fill in all password fields")
            return

        #Run standard registration check password tests
        if not check_password(new_password, self.password_error_lbl):
            return

        #Check that new passwords match
        if not check_confirm_password(confirm_password, new_password, self.password_error_lbl):
            return

        active_user = auth.get_user()
        if not active_user:
            self.password_error_lbl.config(text="Session expired. Please log in again.")
            return

        con = database.connect()
        if con is None:
            self.password_error_lbl.config(text="Could not connect to database")
            return

        try:
            cur = con.cursor()

            #Retrieve user's current hashed password from database to verify identity
            cur.execute("SELECT password FROM users WHERE id = ?", (active_user.id,))
            db_row = cur.fetchone()
            if db_row is None:
                self.password_error_lbl.config(text="User record not found")
                return

            db_password_hash = db_row[0]

            #Hash old password input using SHA-256 and match it against DB hash
            hashed_old_input = hashlib.sha256(old_password.encode()).hexdigest()

            if hashed_old_input != db_password_hash:
                self.password_error_lbl.config(text="Incorrect old password")
                return

            #Hash new password and update database record
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            cur.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_new_password, active_user.id))
            con.commit()

            #Reset input field values on success
            self.old_password_entry.delete(0, tk.END)
            self.new_password_entry.delete(0, tk.END)
            self.confirm_password_entry.delete(0, tk.END)

            messagebox.showinfo("Success", "Password updated successfully!")

        except Exception as e:
            logging.exception("Error updating password")
            self.password_error_lbl.config(text="Error updating password")
        finally:
            con.close()
