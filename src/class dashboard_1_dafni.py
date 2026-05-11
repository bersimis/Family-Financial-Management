import tkinter as tk
from tkinter import messagebox

import session
from transactions import TransactionsFrame
from categories import CategoriesWindow


class Dashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Family Finance Management - Dashboard")
        self.root.geometry("950x600")
        self.root.resizable(False, False)

        self.sidebar = tk.Frame(self.root, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")

        self.main_area = tk.Frame(self.root, bg="white")
        self.main_area.pack(side="right", expand=True, fill="both")

        self.create_sidebar()
        self.show_home()

        self.root.mainloop()

    def create_sidebar(self):
        title = tk.Label(
            self.sidebar,
            text="Finance App",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=20)

        username = getattr(session, "current_username", "User")
        user_label = tk.Label(
            self.sidebar,
            text=f"Welcome,\n{username}",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 11)
        )
        user_label.pack(pady=10)

        tk.Button(
            self.sidebar,
            text="Dashboard",
            width=20,
            command=self.show_home
        ).pack(pady=8)

        tk.Button(
            self.sidebar,
            text="Transactions",
            width=20,
            command=self.show_transactions
        ).pack(pady=8)

        tk.Button(
            self.sidebar,
            text="Categories",
            width=20,
            command=self.open_categories
        ).pack(pady=8)

        tk.Button(
            self.sidebar,
            text="Exit",
            width=20,
            command=self.exit_app
        ).pack(pady=30)

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_main_area()

        tk.Label(
            self.main_area,
            text="Family Finance Management",
            bg="white",
            font=("Arial", 22, "bold")
        ).pack(pady=40)

        tk.Label(
            self.main_area,
            text="Use the menu on the left to manage your transactions and categories.",
            bg="white",
            font=("Arial", 13)
        ).pack(pady=10)

    def show_transactions(self):
        self.clear_main_area()
        TransactionsFrame(self.main_area)

    def open_categories(self):
        CategoriesWindow(self.root)

    def exit_app(self):
        answer = messagebox.askyesno("Exit", "Do you want to exit the application?")
        if answer:
            self.root.destroy()


if __name__ == "__main__":
    Dashboard()
