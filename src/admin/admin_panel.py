#Admin Panel
#This file handles the GUI and all admin-specific capabilities
import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
import logging
from database import database
import config_and_styles as style

class AdminPanelFrame:
    def __init__(self, parent):
        #Store the parent frame (main_area of Dashboard)
        self.parent = parent

        #Create the main container frame for the admin panel
        self.frame = tk.Frame(parent, bg=style.COLOR_BG_MAIN)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        #Initialize selection variables
        self.selected_user_id = None
        self.selected_username = None

        #Build the user interface
        self.create_widgets()
        
        #Load registered users from database
        self.load_users()
        #Load roles for the dropdown
        self.load_roles()

    def create_widgets(self):
        #Create title label
        title = tk.Label(
            self.frame,
            text="ADMIN PANEL - USER MANAGEMENT",
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, 20, "bold")
        )
        title.pack(pady=15)

        #Define table columns
        columns = ("id", "username", "role")

        #Create Treeview table to display users
        self.tree = ttk.Treeview(
            self.frame,
            columns=columns,
            show="headings",
            height=10
        )

        #Create table headings
        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Username")
        self.tree.heading("role", text="Role / Privilege")

        #Set table column widths and alignments
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("username", width=250, anchor="w")
        self.tree.column("role", width=180, anchor="center")

        #Pack the table onto the frame
        self.tree.pack(pady=15, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self.on_user_select)

        #Actions Panel (Card Frame)
        self.action_card = tk.LabelFrame(
            self.frame,
            text="User Actions",
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON, "bold"),
            padx=15,
            pady=15
        )
        self.action_card.pack(fill="x", pady=10)

        #Selected User Label
        self.user_label = tk.Label(
            self.action_card,
            text="Selected User: None",
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT, "bold")
        )
        self.user_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        #Role Combobox Label
        tk.Label(
            self.action_card,
            text="Select New Role:",
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
        ).grid(row=1, column=0, sticky="w", padx=(0, 10))

        #Role Combobox
        self.role_var = tk.StringVar()
        self.role_combo = ttk.Combobox(
            self.action_card,
            textvariable=self.role_var,
            state="readonly",
            width=20,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
        )
        self.role_combo.grid(row=1, column=1, sticky="w")

        #Update Role Button
        self.btn_update_role = tk.Button(
            self.action_card,
            text="Change Role",
            bg=style.COLOR_PRIMARY,
            fg=style.COLOR_LIGHT,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON, "bold"),
            command=self.update_user_role,
            width=15
        )
        self.btn_update_role.grid(row=1, column=2, padx=20)

        #Reset Password Button
        self.btn_reset_pwd = tk.Button(
            self.action_card,
            text="Reset Password",
            bg=style.COLOR_DANGER,
            fg=style.COLOR_LIGHT,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON, "bold"),
            command=self.reset_user_password,
            width=15
        )
        self.btn_reset_pwd.grid(row=1, column=3, padx=10)

    def load_users(self):
        #Clear any existing rows in the table
        for row in self.tree.get_children():
            self.tree.delete(row)

        con = database.connect()
        if con is None:
            return

        try:
            cur = con.cursor()
            
            #Get user details along with their role name
            cur.execute("""
                SELECT users.id, users.username, roles.name
                FROM users
                INNER JOIN roles 
                ON users.role_id = roles.id
                ORDER BY users.id ASC
            """)
            
            users = cur.fetchall()

            #Insert users into the Treeview
            for user in users:
                self.tree.insert("", tk.END, values=user)

        except Exception as error:
            logging.exception("Failed to load users in admin panel.")
            messagebox.showerror("Error", f"Failed to load users:\n{error}")

        finally:
            con.close()

    def load_roles(self):
        con = database.connect()
        if con is None:
            return

        try:
            cur = con.cursor()
            cur.execute("SELECT id, name FROM roles")
            roles_data = cur.fetchall()
            
            #Map role names to their database IDs dynamically
            self.roles_map = {name: role_id for role_id, name in roles_data}
            
            #Populates dropdown list values
            self.role_combo["values"] = list(self.roles_map.keys())

        except Exception as error:
            logging.exception("Failed to load roles in admin panel.")
            messagebox.showerror("Error", f"Failed to load roles:\n{error}")

        finally:
            con.close()

    def on_user_select(self, event):
        #Get the selected row in the Treeview
        selected_item = self.tree.selection()
        if not selected_item:
            return

        #Extract values of the selected user row
        item_values = self.tree.item(selected_item)["values"]
        self.selected_user_id = item_values[0]
        self.selected_username = item_values[1]
        user_role = item_values[2]

        #Update the UI labels
        self.user_label.config(text=f"Selected User: {self.selected_username}")
        self.role_var.set(user_role)

    def update_user_role(self):
        if not self.selected_user_id:
            messagebox.showwarning("Warning", "Please select a user first.")
            return

        new_role_name = self.role_var.get()
        if not new_role_name:
            messagebox.showwarning("Warning", "Please select a role.")
            return

        #Get database ID for the selected role name
        new_role_id = self.roles_map.get(new_role_name)

        con = database.connect()
        if con is None:
            return

        try:
            cur = con.cursor()
            cur.execute("""
                UPDATE users
                SET role_id = ?
                WHERE id = ?
            """, (new_role_id, self.selected_user_id))
            con.commit()

            messagebox.showinfo("Success", f"Role updated successfully for user {self.selected_username}.")
            
            #Refresh list
            self.load_users()

        except Exception as error:
            logging.exception("Failed to update user role in admin panel.")
            messagebox.showerror("Error", f"Failed to update role:\n{error}")

        finally:
            con.close()

    def reset_user_password(self):
        if not self.selected_user_id:
            messagebox.showwarning("Warning", "Please select a user first.")
            return

        #Confirm the action before resetting
        confirm = messagebox.askyesno(
            "Confirm Reset", 
            f"Are you sure you want to reset password for user '{self.selected_username}' to 'admin'?"
        )
        if not confirm:
            return

        #Hash 'admin' using SHA-256 (matches the database hash function)
        hashed_password = hashlib.sha256(b"admin").hexdigest()

        con = database.connect()
        if con is None:
            return

        try:
            cur = con.cursor()
            cur.execute("""
                UPDATE users
                SET password = ?
                WHERE id = ?
            """, (hashed_password, self.selected_user_id))
            con.commit()

            #Display exact requested messagebox notification
            messagebox.showinfo("Success", "password reseted")

        except Exception as error:
            logging.exception("Failed to reset user password in admin panel.")
            messagebox.showerror("Error", f"Failed to reset password:\n{error}")

        finally:
            con.close()
