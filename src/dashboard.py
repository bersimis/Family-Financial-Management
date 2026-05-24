# Dashboard.py
# This py file will handle the dashboard section and main application shell.
# This is the entry point; all file paths and views are routed from here.
import os
import logging
import tkinter as tk
from tkinter import messagebox
#Import database module to communicate with SQLite database
from database import database
#Import auth module to manage logged-in user session
from login_system import auth
from login_system import login
#Import GUIs
from finance_files.transactions import TransactionsFrame
from finance_files.categories import CategoriesWindow
from admin import admin_panel
#Import global configuration and styles
import config_and_styles as style



#-------------------------------------------------------------------------
#Set up logging for error collection
def setup_logging():
    #Create logs directory if it does not exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logging.basicConfig(
        filename=os.path.join("logs", "app.log"),
        level=logging.ERROR,
        format='%(asctime)s | %(levelname)s | %(message)s | %(module)s'
    )


#-------------------------------------------------------------------------
#Main class responsible for the main window and top-level UI shell
class Dashboard:

    def __init__(self, root):
        self.root = root

        #Apply global background color to root window
        self.root.configure(bg=style.COLOR_BG_MAIN)

        #Clear existing widgets from root (e.g. from login screen).
        for widget in self.root.winfo_children():
            widget.destroy()

        #Create the left navigation sidebar
        self.sidebar = tk.Frame(
            self.root,
            bg=style.COLOR_PRIMARY,
            width=220
        )
        self.sidebar.pack(side="left", fill="y")

        #Create the main content area on the right
        self.main_area = tk.Frame(
            self.root,
            bg=style.COLOR_BG_MAIN
        )
        self.main_area.pack(side="right", expand=True, fill="both")

        #Build sidebar buttons
        self.create_sidebar()

        #Show the default dashboard view
        self.show_dashboard()

    #Create sidebar navigation controls
    def create_sidebar(self):
        #Application title in sidebar
        title = tk.Label(
            self.sidebar,
            text=style.APP_TITLE,
            bg=style.COLOR_PRIMARY,
            fg=style.COLOR_LIGHT,
            font=(style.FONT_FAMILY, 16, "bold"),
            wraplength=180,
            justify="center"
        )
        title.pack(pady=25)

        #Display currently logged-in user
        active_user = auth.get_user()
        username = active_user.username

        user_label = tk.Label(
            self.sidebar,
            text=f"User: {username}",
            bg=style.COLOR_PRIMARY,
            fg=style.COLOR_LIGHT,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
        )
        user_label.pack(pady=10)

        #Sidebar Buttons
        tk.Button(
            self.sidebar,
            text="Dashboard",
            width=20,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON),
            command=self.show_dashboard
        ).pack(pady=8)

        tk.Button(
            self.sidebar,
            text="Transactions",
            width=20,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON),
            command=self.show_transactions
        ).pack(pady=8)

        
        tk.Button(
            self.sidebar,
            text="Profile",
            width=20,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON),
            command=self.show_dashboard
        ).pack(pady=(8,50))


        if active_user.role_id == 1:
            tk.Button(
                self.sidebar,
                text="Admin Panel",
                width=20,
                font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON),
                command=self.show_admin_panel
            ).pack(pady=8)
        
        tk.Button(
            self.sidebar,
            text="Logout",
            width=20,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON),
            command=self.logout
        ).pack(pady=8)
        
        tk.Button(
            self.sidebar,
            text="Exit",
            width=20,
            font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON),
            command=self.exit_app
        ).pack(pady=8)

    #Helper method to clear main content area,if deleting files is required
    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    #Calculate financial summary: total income, total expenses, and balance
    def get_financial_summary(self):
        con = database.connect()
        if con is None:
            return 0, 0, 0

        try:
            cur = con.cursor()
            active_user = auth.get_user()
            user_id = active_user.id if active_user is not None else 1

            #Fetch sum of all income transactions for this user
            cur.execute("""
                SELECT SUM(transactions.amount)
                FROM transactions
                INNER JOIN categories
                ON transactions.category_id = categories.id
                WHERE categories.type = 'income'
                AND transactions.created_by = ?
            """, (user_id,))
            total_income = cur.fetchone()[0]

            #fetch sum of all expense transactions for this user
            cur.execute("""
                SELECT SUM(transactions.amount)
                FROM transactions
                INNER JOIN categories
                ON transactions.category_id = categories.id
                WHERE categories.type = 'expense'
                AND transactions.created_by = ?
            """, (user_id,))
            total_expenses = cur.fetchone()[0]

            if total_income is None:
                total_income = 0.0

            if total_expenses is None:
                total_expenses = 0.0

            balance = total_income - total_expenses
            return total_income, total_expenses, balance

        except Exception as e:
            logging.exception("An error occurred while calculating the financial summary.")
            return 0.0, 0.0, 0.0
        finally:
            con.close()


    def get_family_financial_summary(self):
        con = database.connect()

        if con is None:
            return 0.0, 0.0, 0.0

        try:
            cur = con.cursor()

            cur.execute("""
                SELECT SUM(transactions.amount)
                FROM transactions
                INNER JOIN categories
                ON transactions.category_id = categories.id
                WHERE categories.type = 'income'
            """)
            family_income = cur.fetchone()[0] or 0.0

            cur.execute("""
                SELECT SUM(transactions.amount)
                FROM transactions
                INNER JOIN categories
                ON transactions.category_id = categories.id
                WHERE categories.type = 'expense'
                """)
            family_expenses = cur.fetchone()[0] or 0.0

            family_balance = family_income - family_expenses

            return family_income, family_expenses, family_balance

        except Exception as e:
            logging.exception("An error occurred while calculating the family financial summary.")
            return 0.0, 0.0, 0.0

        finally:
            con.close()
    

    #Display dashboard stats and cards, create class Dashboard
            
    def show_dashboard(self):
        #Clear main panel first
        self.clear_main_area()

        #Retrieve financial data
        total_income, total_expenses, balance = self.get_financial_summary()
        
        #Add family financial data
        family_income, family_expenses, family_balance = self.get_family_financial_summary()
        
        #Title Label
        tk.Label(
            self.main_area,
            text="Dashboard",
            bg=style.COLOR_BG_MAIN,
            fg=style.COLOR_TEXT_MAIN,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TITLE, "bold")
        ).pack(pady=30)

        #Cards Frame
        cards_frame = tk.Frame(
             self.main_area,
             bg=style.COLOR_BG_MAIN
         )
        cards_frame.pack(pady=20)
    

        #Total Income Card
        self.create_card(
            cards_frame,
            "Total Income",
            f"{total_income:.2f} €",
            style.COLOR_SUCCESS,
            0,
            0
        )

        #Total Expenses Card
        self.create_card(
            cards_frame,
            "Total Expenses",
            f"{total_expenses:.2f} €",
            style.COLOR_DANGER,
            0,
            1
        )

        #Current Balance Card
        self.create_card(
            cards_frame,
            "Current Balance",
            f"{balance:.2f} €",
            style.COLOR_PRIMARY,
            0,
            2
        )


   #Family income-expenses, balance tabs
    

        self.create_card(
            cards_frame,
            "Family Income",
            f"{family_income:.2f} €",
            style.COLOR_SUCCESS,
            1,
            0
            )

        self.create_card(
            cards_frame,
            "Family Expenses",
            f"{family_expenses:.2f} €",
            style.COLOR_DANGER,
            1,
            1
            )

        self.create_card(
            cards_frame,
            "Family Balance",
            f"{family_balance:.2f} €",
            style.COLOR_PRIMARY,
            1,
            2
            )

        #Informational subtext
        tk.Label(
              self.main_area,
              text="Use the menu on the left to manage transactions and categories.",
              bg=style.COLOR_BG_MAIN,
              fg=style.COLOR_TEXT_MUTED,
              font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT)
          ).pack(pady=30)

    #Dynamic card generation
    def create_card(self, parent, title, value, value_color, row, column):
        card = tk.Frame(
            parent,
            bg=style.COLOR_BG_CARD,
            width=220,
            height=130,
            relief="ridge",
            borderwidth=1
        )
        card.grid(row=row, column=column, padx=15, pady=10)
        card.pack_propagate(False)

        #Card Title
        tk.Label(
            card,
            text=title,
            bg=style.COLOR_BG_CARD,
            fg=style.COLOR_TEXT_MUTED,
            font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT, "bold")
        ).pack(pady=18)

        #Card Value
        tk.Label(
            card,
            text=value,
            bg=style.COLOR_BG_CARD,
            fg=value_color,
            font=(style.FONT_FAMILY, 20, "bold")
        ).pack(pady=10)

    #Navigate to Transactions View
    def show_transactions(self):
        self.clear_main_area()
        TransactionsFrame(self.main_area)

    #Navigate to Admin Panel View
    def show_admin_panel(self):
        self.clear_main_area()
        from admin.admin_panel import AdminPanelFrame
        AdminPanelFrame(self.main_area)

    #Open Categories Window
    def open_categories(self):
        CategoriesWindow(self.root)

    #Safely close application with user prompt
    def exit_app(self):
        answer = messagebox.askyesno(
            "Exit",
            "Do you want to exit the application?"
        )
        if answer:
            self.root.destroy()

    #destroy/logout user and redirect him to login page        
    def logout(self):
        answer = messagebox.askyesno(
            "Logout",
            "Do you want to Logout?"
        )
        if answer:
            auth.destroy_user()
            login.build_login_gui(self.root)


#-------------------------------------------------------------------------
#Legacy routing compatibility for other modules
def build_dashboard_gui(root):
    Dashboard(root)

#-------------------------------------------------------------------------
#Main function of the program.
def main():
    setup_logging()  #Start error logger
    try:
        #Create and initialize main application root window
        root = tk.Tk()
        root.title(style.APP_TITLE)
        root.geometry(style.APP_DIMENSIONS)
        root.resizable(False, False)

        con = database.connect()  #Connect to SQLite database
        if con:
            logged_in = auth.check_login()  #Check user session status
            if logged_in:
                Dashboard(root)
            else:
                login.build_login_gui(root)
        else:
            print("There was a problem while connecting to the database.")

        #Run primary Tkinter GUI loop
        root.mainloop()

    except Exception as e:
        logging.exception("Critical Error: The application crashed.")


if __name__ == "__main__":
    main()
