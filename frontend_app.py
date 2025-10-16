# File: frontend_app.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import json
import urllib.request
import urllib.parse
import urllib.error

BACKEND_URL = "http://127.0.0.1:8000/api/expenses"

def get_expenses_from_api(search_query=None):
    url = BACKEND_URL
    if search_query:
        params = urllib.parse.urlencode({'q': search_query})
        url = f"{BACKEND_URL}?{params}"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        messagebox.showerror("Connection Error", f"Could not connect to the backend.\nPlease ensure backend_server.py is running.\n\nError: {e.reason}")
        return []

def add_expense_to_api(expense_data):
    try:
        data = json.dumps(expense_data).encode('utf-8')
        req = urllib.request.Request(BACKEND_URL, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req) as response:
            return response.status in [200, 201]
    except urllib.error.URLError as e:
        messagebox.showerror("Connection Error", f"Failed to add expense.\nError: {e.reason}")
        return False

def add_expense_action():
    if not all([e_date.get(), e_place.get(), e_amount.get()]):
        messagebox.showwarning("Input Error", "Date, Item, and Amount are required.")
        return
    try:
        expense_data = {"date": e_date.get(), "item": e_place.get(), "amount": float(e_amount.get()), "utr": e_utr.get()}
        if add_expense_to_api(expense_data):
            show_view_screen()
    except ValueError:
        messagebox.showerror("Invalid Input", "Amount must be a number.")

def search_expenses(event=None):
    query = search_entry.get()
    expenses = get_expenses_from_api(query)
    populate_tree(expenses)

def populate_tree(data):
    for item in tree.get_children():
        tree.delete(item)
    total = 0.0
    for expense in data:
        values = (expense['date'], expense['item'], expense['amount'], expense.get('utr', ''))
        tree.insert("", tk.END, values=values)
        total += float(expense['amount'])
    total_label.config(text=f"Total Spent: {total:,.2f}")

def sort_column(col_name, reverse):
    data = [(tree.set(child, col_name), child) for child in tree.get_children('')]
    if col_name == "Amount":
        data.sort(key=lambda item: float(item[0]), reverse=reverse)
    else:
        data.sort(reverse=reverse)
    for index, (val, child) in enumerate(data):
        tree.move(child, '', index)
    tree.heading(col_name, command=lambda: sort_column(col_name, not reverse))

def show_view_screen():
    add_frame.grid_forget()
    show_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    search_expenses()

def show_add_screen():
    show_frame.grid_forget()
    add_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    e_date.delete(0, tk.END)
    e_date.insert(0, date.today().strftime('%d-%m-%Y'))
    e_place.delete(0, tk.END)
    e_amount.delete(0, tk.END)
    e_utr.delete(0, tk.END)
    e_place.focus_set()

root = tk.Tk()
root.title("Expense Tracker")
root.geometry("800x600")
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
style = ttk.Style(root)
style.theme_use('clam')
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("Total.TLabel", font=("Segoe UI", 12, "bold"))
nav_frame = ttk.Frame(root)
nav_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,0))
ttk.Button(nav_frame, text="Add Expense", command=show_add_screen).pack(side="left")
ttk.Button(nav_frame, text="View Expenses", command=show_view_screen).pack(side="left", padx=5)
content_container = ttk.Frame(root)
content_container.grid(row=1, column=0, sticky="nsew")
add_frame = ttk.Frame(content_container, padding=20)
show_frame = ttk.Frame(content_container, padding=20)
show_frame.columnconfigure(0, weight=1)
show_frame.rowconfigure(1, weight=1)
form_frame = ttk.LabelFrame(add_frame, text="Expense Details", padding=20)
form_frame.pack(fill="x", expand=True)
form_frame.columnconfigure(1, weight=1)
ttk.Label(form_frame, text="Item/Place:").grid(row=0, column=0, sticky="w", pady=5)
e_place = ttk.Entry(form_frame, width=40)
e_place.grid(row=0, column=1, sticky="ew")
ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, sticky="w", pady=5)
e_amount = ttk.Entry(form_frame, width=40)
e_amount.grid(row=1, column=1, sticky="ew")
ttk.Label(form_frame, text="Date:").grid(row=2, column=0, sticky="w", pady=5)
e_date = ttk.Entry(form_frame, width=40)
e_date.grid(row=2, column=1, sticky="ew")
ttk.Label(form_frame, text="UTR/Note:").grid(row=3, column=0, sticky="w", pady=5)
e_utr = ttk.Entry(form_frame, width=40)
e_utr.grid(row=3, column=1, sticky="ew")
ttk.Button(add_frame, text="Submit Expense", command=add_expense_action).pack(pady=20)
search_bar = ttk.Frame(show_frame)
search_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
ttk.Label(search_bar, text="Search:").pack(side="left", padx=(0, 5))
search_entry = ttk.Entry(search_bar)
search_entry.pack(side="left", fill="x", expand=True)
search_entry.bind("<KeyRelease>", search_expenses)
tree_frame = ttk.Frame(show_frame)
tree_frame.grid(row=1, column=0, sticky="nsew")
tree_frame.columnconfigure(0, weight=1)
tree_frame.rowconfigure(0, weight=1)
tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
columns = ("Date", "Item", "Amount", "UTR")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=tree_scroll.set)
tree_scroll.config(command=tree.yview)
for col in columns:
    tree.heading(col, text=col, command=lambda c=col: sort_column(c, False))
tree.column("Amount", anchor="e")
tree_scroll.grid(row=0, column=1, sticky="ns")
tree.grid(row=0, column=0, sticky="nsew")
total_label = ttk.Label(show_frame, text="Total Spent:", style="Total.TLabel")
total_label.grid(row=2, column=0, sticky="e", pady=10)
show_view_screen()
root.mainloop()