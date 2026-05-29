#export.py
import pandas as pd
from tkinter import filedialog, messagebox
from database import database

def export_to_excel(user_id):
    con = database.connect()
    try:
        # Extracting data with SQL JOIN
        query = """
            SELECT t.date as 'Ημ/νία', c.type as 'Τύπος', c.name as 'Κατηγορία', 
                   t.amount as 'Ποσό', t.is_monthly as 'Μηνιαίο', u.username as 'Χρήστης'
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            JOIN users u ON t.created_by = u.id
            WHERE t.created_by = ? ORDER BY t.date DESC
        """

        df = pd.read_sql_query(query, con, params=(user_id,))
        
        # Open storage window
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title="Αποθήκευση ως Excel"
        )
        
        if filepath:
            df.to_excel(filepath, index=False)
            messagebox.showinfo("Επιτυχία", "Η εξαγωγή ολοκληρώθηκε επιτυχώς!")
            
    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Αποτυχία εξαγωγής: {e}")
    finally:
        con.close()