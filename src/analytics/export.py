#export.py
import pandas as pd
import logging
from tkinter import filedialog, messagebox
from database import database

def export_to_excel(user_id=None):
    con = database.connect()
    try:
        #Extracting data with SQL JOIN
        if user_id is not None:
            query = """
                SELECT t.date as 'Date', c.type as 'Type', c.name as 'Category', 
                       t.amount as 'Amount', t.is_monthly as 'Monthly', u.username as 'User'
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                JOIN users u ON t.created_by = u.id
                WHERE t.created_by = ? ORDER BY t.date DESC
            """
            df = pd.read_sql_query(query, con, params=(user_id,))
        else:
            query = """
                SELECT t.date as 'Date', c.type as 'Type', c.name as 'Category', 
                       t.amount as 'Amount', t.is_monthly as 'Monthly', u.username as 'User'
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                JOIN users u ON t.created_by = u.id
                ORDER BY t.date DESC
            """
            df = pd.read_sql_query(query, con)
        
        #Open storage window
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title="Save as Excel"
        )
        
        if filepath:
            df.to_excel(filepath, index=False)
            messagebox.showinfo("Success", "Export completed successfully!")
            
    except Exception as e:
        logging.exception("Error exporting transactions to Excel.")
        messagebox.showerror("Error", f"Export failed: {e}")
    finally:
        con.close()