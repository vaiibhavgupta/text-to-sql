import sqlite3
import time
def run_query(db, query, split='dev'):
    with sqlite3.connect(f'file:./dataset/{split}_set/{split}_databases/{db}/{db}.sqlite?mode=ro', uri=True) as conn:
        cursor = conn.cursor()
        try:
            start = time.time()
            cursor.execute(query)
            result = cursor.fetchall()
            end = time.time()
            return result, round(end-start, 4)
        except Exception as oe:
            return f"ERROR: {oe}", -1