import sqlite3
import os

DB_PATH = "data/gantry.db"


def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check Messages table for cl_id
    cursor.execute("PRAGMA table_info(messages)")
    columns = [row[1] for row in cursor.fetchall()]
    if "cl_id" in columns:
        print("PASS: 'cl_id' column exists in 'messages' table.")
    else:
        print("FAIL: 'cl_id' column MISSING in 'messages' table.")

    # Check Feedback table
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'"
    )
    if cursor.fetchone():
        print("PASS: 'feedback' table exists.")
    else:
        print("FAIL: 'feedback' table MISSING.")

    conn.close()


if __name__ == "__main__":
    check_schema()
