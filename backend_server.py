# File: backend_server.py
import http.server
import socketserver
import json
import sqlite3
from urllib.parse import urlparse, parse_qs

PORT = 8000


def db_connection():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn


class ExpenseRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/api/expenses':
            query_components = parse_qs(parsed_path.query)
            search_term = query_components.get('q', [None])[0]
            try:
                conn = db_connection()
                cursor = conn.cursor()
                if search_term:
                    sql = "SELECT date, item, amount, utr FROM expenses WHERE item LIKE ? OR utr LIKE ? ORDER BY id DESC"
                    like_query = f"%{search_term}%"
                    cursor.execute(sql, (like_query, like_query))
                else:
                    sql = "SELECT date, item, amount, utr FROM expenses ORDER BY id DESC"
                    cursor.execute(sql)

                expenses = [dict(row) for row in cursor.fetchall()]
                conn.close()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(expenses).encode('utf-8'))
            except Exception as e:
                self.send_error(500, f"Server Error: {e}")
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == '/api/expenses':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                conn = db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO expenses (date, item, amount, utr) VALUES (?, ?, ?, ?)",
                    (data['date'], data['item'], float(data['amount']), data.get('utr', ''))
                )
                conn.commit()
                conn.close()
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"message": "Expense added successfully"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_error(500, f"Server Error: {e}")
        else:
            self.send_error(404, "Not Found")


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), ExpenseRequestHandler) as httpd:
        print(f"Backend server running on http://localhost:{PORT}")
        httpd.serve_forever()