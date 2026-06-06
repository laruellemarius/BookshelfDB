import sqlite3
import os

# ---------------- SAFE DB PATH (IMPORTANT FOR EXE) ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "books.db")


def connect():
    return sqlite3.connect(DB_PATH)


# ---------------- TABLE ----------------

conn = connect()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    author TEXT,
    genre TEXT,
    status TEXT,
    price REAL NOT NULL,
    favorite INTEGER DEFAULT 0
)
""")

conn.commit()


# ---------------- CREATE ----------------

def addBook(name, author, genre, status, price):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO books (name, author, genre, status, price, favorite)
    VALUES (?, ?, ?, ?, ?, 0)
    """, (name, author, genre, status, price))

    conn.commit()
    conn.close()


# ---------------- READ ----------------

def getBooks():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()

    conn.close()
    return rows


# ---------------- DELETE ----------------

def deleteBook(book_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()


# ---------------- UPDATE STATUS ----------------

def updateStatus(book_id, new_status):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE books
    SET status = ?
    WHERE id = ?
    """, (new_status, book_id))

    conn.commit()
    conn.close()


# ---------------- TOGGLE FAVORITE ----------------

def toggleFavorite(book_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE books
    SET favorite = CASE
        WHEN favorite = 1 THEN 0
        ELSE 1
    END
    WHERE id = ?
    """, (book_id,))

    conn.commit()
    conn.close()


# ---------------- FULL UPDATE ----------------

def updateBook(book_id, name, author, genre, status, price):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE books
    SET name = ?, author = ?, genre = ?, status = ?, price = ?
    WHERE id = ?
    """, (name, author, genre, status, price, book_id))

    conn.commit()
    conn.close()