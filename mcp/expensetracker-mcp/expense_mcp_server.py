import os
import sqlite3
from mcp.server.fastmcp import FastMCP

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'expenses.db')

mcp = FastMCP("ExpenseTracker")

def init_db():
    """Initializes the SQLite database and creates the expenses table if it does not exist."""
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)
        c.commit()

init_db()

@mcp.tool()
def add_expense(date: str, thread_id: str, amount: float, category: str, subcategory: str, note: str = "") -> dict:
    """
    Add a new expense entry to the database.
    Format the date as YYYY-MM-DD.
    """
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute(
            "INSERT INTO expenses(date, thread_id, amount, category, subcategory, note) VALUES (?,?,?,?,?,?)",
            (date, thread_id, amount, category, subcategory, note)
        )
        c.commit()
        return {"status": "ok", "id": cur.lastrowid}
    
@mcp.tool()
def list_expenses(start_date: str, end_date: str, category: str = "") -> list:
    '''List expense entries within an inclusive date range. Optionally filter by category.'''
    with sqlite3.connect(DB_PATH) as c:
        query = """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        
        if category:
            query += " AND category = ?"
            params.append(category)
            
        query += " ORDER BY id ASC"
        
        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

@mcp.tool()
def summarize(start_date: str, end_date: str, category: str = "") -> list:
    '''Summarize expenses by category within an inclusive date range.'''
    with sqlite3.connect(DB_PATH) as c:
        # Define the base query string first
        query = """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses 
            WHERE date BETWEEN ? AND ?
        """
        
        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"

        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


if __name__ == "__main__":
    mcp.run()