# File: run_windows.py
import subprocess
import time
import os
import sys
import sqlite3
#
def setup_database():
    """Creates the database and table if they don't exist."""
    try:
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
        print("Database checked and ready.")
    except Exception as e:
        print(f"Error setting up database: {e}")
        input("Press Enter to exit.") # So user can see the error
        sys.exit(1)

#
BACKEND_SCRIPT = 'backend_server.py'
FRONTEND_SCRIPT = 'frontend_app.py'

def run_application():
    print("🚀 Launching Expense Tracker for Windows...")

    if not all([os.path.exists(BACKEND_SCRIPT), os.path.exists(FRONTEND_SCRIPT)]):
        print(f"❌ Error: Make sure '{BACKEND_SCRIPT}' and '{FRONTEND_SCRIPT}' are in this folder.")
        input("Press Enter to exit.")
        return
    setup_database()
    python_executable = sys.executable

    try:
        print(f"--> Starting Backend Server ('{BACKEND_SCRIPT}') in a new window...")
        backend_process = subprocess.Popen(
            [python_executable, BACKEND_SCRIPT],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print("--> Backend process started successfully.")
    except Exception as e:
        print(f"❌ Critical Error: Could not start the backend server. {e}")
        input("Press Enter to exit.")
        return

    print("--> Waiting 2 seconds for the server to warm up...")
    time.sleep(2)

    try:
        print(f"--> Starting Frontend UI ('{FRONTEND_SCRIPT}')...")
        frontend_process = subprocess.Popen([python_executable, FRONTEND_SCRIPT])
        print("✅ Application is now running!")
        frontend_process.wait()
    except Exception as e:
        print(f"❌ Critical Error: Could not start the frontend UI. {e}")
    finally:
        print("\n--> Frontend UI closed. Terminating backend server.")
        backend_process.terminate()
        print("--> All processes stopped. Goodbye!")

if __name__ == "__main__":
    run_application()