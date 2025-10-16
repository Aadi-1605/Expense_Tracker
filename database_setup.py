# File: database_setup.py
import sqlite3

conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        item TEXT NOT NULL,
        amount REAL NOT NULL,
        utr TEXT
    )
''')

conn.commit()
conn.close()

print("✅ Database 'expenses.db' created successfully.")