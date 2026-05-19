
# Εισάγουμε τη βιβλιοθήκη tkinter για να δημιουργήσουμε γραφικό περιβάλλον χρήστη.
import tkinter as tk

# Εισάγουμε το messagebox για να εμφανίζουμε μηνύματα επιβεβαίωσης ή σφάλματος.
from tkinter import messagebox

# Εισάγουμε το database module από τον φάκελο database.
# Από εδώ θα χρησιμοποιήσουμε τη συνάρτηση connect() για σύνδεση με τη βάση δεδομένων.
from database import database
#Εισάγουμκε το login module από το system login
from login_system import auth

# Εισάγουμε δεδομένα από το finance files

from finance_files.transactions import TransactionsFrame
from finance_files.categories import CategoriesWindow


# Εισάγουμε από το config_and_styles όλες τις σταθερές που αφορούν:
# τίτλο εφαρμογής, διαστάσεις, χρώματα και γραμματοσειρές.
from config_and_styles import (
    # Τίτλος εφαρμογής.
    APP_TITLE,

    # Διαστάσεις βασικού παραθύρου.
    APP_DIMENSIONS,

    # Βασικό χρώμα φόντου.
    COLOR_BG_MAIN,

    # Χρώμα φόντου για κάρτες.
    COLOR_BG_CARD,

    # Βασικό χρώμα κειμένου.
    COLOR_TEXT_MAIN,

    # Δευτερεύον χρώμα κειμένου.
    COLOR_TEXT_MUTED,

    # Κύριο χρώμα εφαρμογής.
    COLOR_PRIMARY,

    # Χρώμα για θετικές τιμές / income.
    COLOR_SUCCESS,

    # Χρώμα για αρνητικές τιμές / expenses.
    COLOR_DANGER,

    # Ανοιχτό χρώμα για κείμενο πάνω σε σκούρα κουμπιά.
    COLOR_LIGHT,

    # Οικογένεια γραμματοσειράς.
    FONT_FAMILY,

    # Μέγεθος γραμματοσειράς τίτλου.
    FONT_SIZE_TITLE,

    # Μέγεθος απλού κειμένου.
    FONT_SIZE_TEXT,

    # Μέγεθος γραμματοσειράς κουμπιών.
    FONT_SIZE_BUTTON
)


# Δημιουργούμε την κλάση Dashboard.
# Η κλάση αυτή είναι υπεύθυνη για το βασικό παράθυρο της εφαρμογής.
class Dashboard:

    # Ο constructor εκτελείται αυτόματα όταν δημιουργείται αντικείμενο Dashboard.
    def __init__(self):

        # Δημιουργούμε το βασικό παράθυρο της εφαρμογής.
        self.root = tk.Tk()

        # Ορίζουμε τον τίτλο του παραθύρου από το config_and_styles.py.
        self.root.title(APP_TITLE)

        # Ορίζουμε τις διαστάσεις του παραθύρου από το config_and_styles.py.
        self.root.geometry(APP_DIMENSIONS)

        # Απενεργοποιούμε την αλλαγή μεγέθους του παραθύρου.
        self.root.resizable(False, False)

        # Δημιουργούμε το αριστερό sidebar.
        # Εκεί θα μπουν τα κουμπιά πλοήγησης.
        self.sidebar = tk.Frame(
            self.root,
            bg=COLOR_PRIMARY,
            width=220
        )

        # Τοποθετούμε το sidebar στην αριστερή πλευρά.
        self.sidebar.pack(side="left", fill="y")

        # Δημιουργούμε το βασικό δεξί τμήμα της εφαρμογής.
        # Εκεί θα εμφανίζεται το dashboard, οι συναλλαγές κτλ.
        self.main_area = tk.Frame(
            self.root,
            bg=COLOR_BG_MAIN
        )

        # Τοποθετούμε το main_area στη δεξιά πλευρά και του δίνουμε όλο τον διαθέσιμο χώρο.
        self.main_area.pack(side="right", expand=True, fill="both")

        # Καλούμε τη μέθοδο που δημιουργεί τα κουμπιά του sidebar.
        self.create_sidebar()

        # Εμφανίζουμε αρχικά την κεντρική οθόνη dashboard.
        self.show_dashboard()

        # Ξεκινάμε το main loop του Tkinter.
        # Αυτό κρατάει ανοιχτό το παράθυρο.
        self.root.mainloop()

    # Η μέθοδος αυτή δημιουργεί το sidebar με τα κουμπιά πλοήγησης.
    def create_sidebar(self):

        # Δημιουργούμε label για τον τίτλο της εφαρμογής στο sidebar.
        title = tk.Label(
            self.sidebar,
            text=APP_TITLE,
            bg=COLOR_PRIMARY,
            fg=COLOR_LIGHT,
            font=(FONT_FAMILY, 16, "bold"),
            wraplength=180,
            justify="center"
        )

        # Τοποθετούμε τον τίτλο στο sidebar.
        title.pack(pady=25)

        # Παίρνουμε το username από το auth.
        # Αν δεν υπάρχει username, εμφανίζουμε προεπιλεγμένα το "admin".
        username = getattr(auth, "current_username", "admin")

        # Δημιουργούμε label που εμφανίζει τον χρήστη.
        user_label = tk.Label(
            self.sidebar,
            text=f"User: {username}",
            bg=COLOR_PRIMARY,
            fg=COLOR_LIGHT,
            font=(FONT_FAMILY, FONT_SIZE_TEXT)
        )

        # Τοποθετούμε το label του χρήστη στο sidebar.
        user_label.pack(pady=10)

        # Δημιουργούμε κουμπί Dashboard.
        # Όταν πατηθεί, καλεί τη μέθοδο show_dashboard.
        tk.Button(
            self.sidebar,
            text="Dashboard",
            width=20,
            font=(FONT_FAMILY, FONT_SIZE_BUTTON),
            command=self.show_dashboard
        ).pack(pady=8)

        # Δημιουργούμε κουμπί Transactions.
        # Όταν πατηθεί, εμφανίζει την οθόνη συναλλαγών.
        tk.Button(
            self.sidebar,
            text="Transactions",
            width=20,
            font=(FONT_FAMILY, FONT_SIZE_BUTTON),
            command=self.show_transactions
        ).pack(pady=8)

        # Δημιουργούμε κουμπί Categories.
        # Όταν πατηθεί, ανοίγει το παράθυρο διαχείρισης κατηγοριών.
        tk.Button(
            self.sidebar,
            text="Categories",
            width=20,
            font=(FONT_FAMILY, FONT_SIZE_BUTTON),
            command=self.open_categories
        ).pack(pady=8)

        # Δημιουργούμε κουμπί Refresh.
        # Όταν πατηθεί, ανανεώνει το dashboard.
        tk.Button(
            self.sidebar,
            text="Refresh",
            width=20,
            font=(FONT_FAMILY, FONT_SIZE_BUTTON),
            command=self.show_dashboard
        ).pack(pady=8)

        # Δημιουργούμε κουμπί Exit.
        # Όταν πατηθεί, καλεί τη μέθοδο exit_app.
        tk.Button(
            self.sidebar,
            text="Exit",
            width=20,
            font=(FONT_FAMILY, FONT_SIZE_BUTTON),
            command=self.exit_app
        ).pack(pady=30)

    # Η μέθοδος αυτή καθαρίζει το main_area.
    # Χρησιμοποιείται πριν εμφανίσουμε νέα οθόνη.
    def clear_main_area(self):

        # Παίρνουμε όλα τα widgets που υπάρχουν μέσα στο main_area.
        for widget in self.main_area.winfo_children():

            # Καταστρέφουμε κάθε widget ώστε να αδειάσει η περιοχή.
            widget.destroy()

    # Η μέθοδος αυτή υπολογίζει τα οικονομικά σύνολα.
    # Δηλαδή συνολικά έσοδα, συνολικά έξοδα και υπόλοιπο.
    def get_financial_summary(self):

        # Συνδεόμαστε στη βάση δεδομένων μέσω του database.connect().
        con = database.connect()

        # Αν η σύνδεση αποτύχει, επιστρέφουμε μηδενικές τιμές.
        if con is None:
            return 0, 0, 0

        # Δημιουργούμε cursor για να εκτελέσουμε SQL queries.
        cur = con.cursor()

        # Παίρνουμε το id του τρέχοντος χρήστη από το auth.
        # Αν δεν υπάρχει, χρησιμοποιούμε προσωρινά το 1.
        user_id = getattr(auth, "current_user_id", 1)

        # Υπολογίζουμε το άθροισμα όλων των income transactions του χρήστη.
        cur.execute("""
            SELECT SUM(transactions.amount)
            FROM transactions
            INNER JOIN categories
            ON transactions.category_id = categories.id
            WHERE categories.type = 'income'
            AND transactions.created_by = ?
        """, (user_id,))

        # Παίρνουμε το αποτέλεσμα του query για τα έσοδα.
        total_income = cur.fetchone()[0]

        # Υπολογίζουμε το άθροισμα όλων των expense transactions του χρήστη.
        cur.execute("""
            SELECT SUM(transactions.amount)
            FROM transactions
            INNER JOIN categories
            ON transactions.category_id = categories.id
            WHERE categories.type = 'expense'
            AND transactions.created_by = ?
        """, (user_id,))

        # Παίρνουμε το αποτέλεσμα του query για τα έξοδα.
        total_expenses = cur.fetchone()[0]

        # Κλείνουμε τη σύνδεση με τη βάση δεδομένων.
        con.close()

        # Αν δεν υπάρχουν έσοδα, το SUM επιστρέφει None.
        # Το μετατρέπουμε σε 0 για να μη βγάλει σφάλμα.
        if total_income is None:
            total_income = 0

        # Αν δεν υπάρχουν έξοδα, το SUM επιστρέφει None.
        # Το μετατρέπουμε σε 0 για να μη βγάλει σφάλμα.
        if total_expenses is None:
            total_expenses = 0

        # Υπολογίζουμε το υπόλοιπο.
        balance = total_income - total_expenses

        # Επιστρέφουμε τα τρία οικονομικά μεγέθη.
        return total_income, total_expenses, balance

    # Η μέθοδος αυτή εμφανίζει την αρχική οθόνη dashboard.
    def show_dashboard(self):

        # Πρώτα καθαρίζουμε την κεντρική περιοχή.
        self.clear_main_area()

        # Παίρνουμε τα οικονομικά σύνολα από τη βάση.
        total_income, total_expenses, balance = self.get_financial_summary()

        # Δημιουργούμε τίτλο Dashboard.
        tk.Label(
            self.main_area,
            text="Dashboard",
            bg=COLOR_BG_MAIN,
            fg=COLOR_TEXT_MAIN,
            font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold")
        ).pack(pady=30)

        # Δημιουργούμε frame που θα περιέχει τις κάρτες.
        cards_frame = tk.Frame(
            self.main_area,
            bg=COLOR_BG_MAIN
        )

        # Τοποθετούμε το frame των καρτών.
        cards_frame.pack(pady=20)

        # Δημιουργούμε κάρτα για τα συνολικά έσοδα.
        self.create_card(
            cards_frame,
            "Total Income",
            f"{total_income:.2f} €",
            COLOR_SUCCESS,
            0,
            0
        )

        # Δημιουργούμε κάρτα για τα συνολικά έξοδα.
        self.create_card(
            cards_frame,
            "Total Expenses",
            f"{total_expenses:.2f} €",
            COLOR_DANGER,
            0,
            1
        )

        # Δημιουργούμε κάρτα για το τρέχον υπόλοιπο.
        self.create_card(
            cards_frame,
            "Current Balance",
            f"{balance:.2f} €",
            COLOR_PRIMARY,
            0,
            2
        )

        # Εμφανίζουμε ενημερωτικό μήνυμα κάτω από τις κάρτες.
        tk.Label(
            self.main_area,
            text="Use the menu on the left to manage transactions and categories.",
            bg=COLOR_BG_MAIN,
            fg=COLOR_TEXT_MUTED,
            font=(FONT_FAMILY, FONT_SIZE_TEXT)
        ).pack(pady=30)

    # Η μέθοδος αυτή δημιουργεί μία κάρτα οικονομικού μεγέθους.
    def create_card(self, parent, title, value, value_color, row, column):

        # Δημιουργούμε frame που λειτουργεί σαν κάρτα.
        card = tk.Frame(
            parent,
            bg=COLOR_BG_CARD,
            width=220,
            height=130,
            relief="ridge",
            borderwidth=1
        )

        # Τοποθετούμε την κάρτα σε grid.
        card.grid(row=row, column=column, padx=15, pady=10)

        # Απενεργοποιούμε την αυτόματη προσαρμογή μεγέθους.
        # Έτσι η κάρτα κρατάει τις διαστάσεις που ορίσαμε.
        card.pack_propagate(False)

        # Δημιουργούμε label για τον τίτλο της κάρτας.
        tk.Label(
            card,
            text=title,
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_MUTED,
            font=(FONT_FAMILY, FONT_SIZE_TEXT, "bold")
        ).pack(pady=18)

        # Δημιουργούμε label για την τιμή της κάρτας.
        tk.Label(
            card,
            text=value,
            bg=COLOR_BG_CARD,
            fg=value_color,
            font=(FONT_FAMILY, 20, "bold")
        ).pack(pady=10)

    # Η μέθοδος αυτή εμφανίζει την οθόνη συναλλαγών.
    def show_transactions(self):

        # Καθαρίζουμε το main_area.
        self.clear_main_area()

        # Δημιουργούμε και εμφανίζουμε το TransactionsFrame μέσα στο main_area.
        TransactionsFrame(self.main_area)

    # Η μέθοδος αυτή ανοίγει το παράθυρο κατηγοριών.
    def open_categories(self):

        # Δημιουργούμε νέο παράθυρο CategoriesWindow.
        CategoriesWindow(self.root)

    # Η μέθοδος αυτή κλείνει την εφαρμογή.
    def exit_app(self):

        # Εμφανίζουμε μήνυμα επιβεβαίωσης.
        answer = messagebox.askyesno(
            "Exit",
            "Do you want to exit the application?"
        )

        # Αν ο χρήστης πατήσει Yes, κλείνουμε το βασικό παράθυρο.
        if answer:
            self.root.destroy()


# Το παρακάτω εκτελείται μόνο αν τρέξουμε απευθείας αυτό το αρχείο.
if __name__ == "__main__":

    # Δημιουργούμε αντικείμενο Dashboard και ξεκινάει η εφαρμογή.
    Dashboard()
