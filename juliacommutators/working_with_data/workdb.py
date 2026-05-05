import sqlite3
def main():
    # Connect to database (creates file if it doesn’t exist)
    conn = sqlite3.connect("presentations.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for t in tables:
        print(t[0])

    conn.close()

if __name__ == "__main__":
    main()