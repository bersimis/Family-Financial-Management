#charts.py
import tkinter as tk
import logging
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import database
import config_and_styles as style

def get_data(user_id, query_type):
    con = database.connect()
    data = []
    try:
        cur = con.cursor()
        if query_type == 'expense':
            cur.execute("""
                SELECT c.name, SUM(t.amount) FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.created_by = ? AND c.type = 'expense' GROUP BY c.name
            """, (user_id,))
            data = cur.fetchall()
        elif query_type == 'income':
            cur.execute("""
                SELECT c.name, SUM(t.amount) FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.created_by = ? AND c.type = 'income' GROUP BY c.name
            """, (user_id,))
            data = cur.fetchall()
        elif query_type == 'balance':
            #Total Income
            cur.execute("""
                SELECT SUM(t.amount) FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.created_by = ? AND c.type = 'income'
            """, (user_id,))
            inc = cur.fetchone()[0] or 0
            
            #Total Expenses
            cur.execute("""
                SELECT SUM(t.amount) FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.created_by = ? AND c.type = 'expense'
            """, (user_id,))
            exp = cur.fetchone()[0] or 0
            data = [inc, exp]
    except Exception as e:
        logging.exception("Error fetching chart data from database.")
        print(f"Database error: {e}")
    finally:
        con.close()
    return data

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def draw_pie_chart(parent_frame, user_id, chart_type):
    clear_frame(parent_frame)
    data = get_data(user_id, chart_type)
    
    if not data:
        tk.Label(parent_frame, text="No data available.", bg=style.COLOR_BG_MAIN).pack(pady=20)
        return

    labels = [row[0] for row in data]
    sizes = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    fig.patch.set_facecolor(style.COLOR_BG_MAIN)
    
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    title = "Expense Distribution" if chart_type == 'expense' else "Income Distribution"
    ax.set_title(title, fontweight='bold')

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)

def draw_balance_chart(parent_frame, user_id):
    clear_frame(parent_frame)
    data = get_data(user_id, 'balance')
    
    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    fig.patch.set_facecolor(style.COLOR_BG_MAIN)
    ax.set_facecolor(style.COLOR_BG_MAIN)

    labels = ['Income', 'Expenses']
    colors = ['#198754', '#dc3545'] #GreenAndRed
    
    ax.bar(labels, data, color=colors, width=0.5)
    ax.set_title("Income - Expense Comparison", fontweight='bold')
    ax.set_ylabel("Amount (€)")

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)


def get_family_data(query_type):
    con = database.connect()
    data = []
    try:
        cur = con.cursor()
        if query_type == 'expense':
            cur.execute("""
                SELECT c.name, SUM(t.amount) FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE c.type = 'expense' GROUP BY c.name
            """)
            data = cur.fetchall()
        elif query_type == 'income':
            cur.execute("""
                SELECT c.name, SUM(t.amount) FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE c.type = 'income' GROUP BY c.name
            """)
            data = cur.fetchall()
        elif query_type == 'balance':
            #TotalFamilyIncome
            cur.execute("""
                SELECT SUM(t.amount) FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE c.type = 'income'
            """)
            inc = cur.fetchone()[0] or 0
            
            #TotalFamilyExpenses
            cur.execute("""
                SELECT SUM(t.amount) FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE c.type = 'expense'
            """)
            exp = cur.fetchone()[0] or 0
            data = [inc, exp]
    except Exception as e:
        logging.exception("Error fetching family chart data.")
        print(f"Database error: {e}")
    finally:
        con.close()
    return data

def draw_family_pie_chart(parent_frame, chart_type):
    clear_frame(parent_frame)
    data = get_family_data(chart_type)
    
    if not data:
        tk.Label(parent_frame, text="No family data available.", bg=style.COLOR_BG_MAIN).pack(pady=20)
        return

    labels = [row[0] for row in data]
    sizes = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    fig.patch.set_facecolor(style.COLOR_BG_MAIN)
    
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    title = "Family Expense Distribution" if chart_type == 'expense' else "Family Income Distribution"
    ax.set_title(title, fontweight='bold', color=style.COLOR_TEXT_MAIN)

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)

def draw_family_balance_chart(parent_frame):
    clear_frame(parent_frame)
    data = get_family_data('balance')
    
    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    fig.patch.set_facecolor(style.COLOR_BG_MAIN)
    ax.set_facecolor(style.COLOR_BG_MAIN)

    labels = ['Total Income', 'Total Expenses']
    colors = ['#198754', '#dc3545'] #GreenAndRed
    
    ax.bar(labels, data, color=colors, width=0.5)
    ax.set_title("Family Income - Expense Comparison", fontweight='bold', color=style.COLOR_TEXT_MAIN)
    ax.set_ylabel("Amount (€)", color=style.COLOR_TEXT_MAIN)
    ax.tick_params(colors=style.COLOR_TEXT_MAIN)

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)