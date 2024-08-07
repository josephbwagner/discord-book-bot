import sqlite3

conn = sqlite3.connect('books.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE users (
                 id INTEGER PRIMARY KEY,
                 discord_id TEXT UNIQUE,
                 points REAL DEFAULT 0
             )''')

c.execute('''CREATE TABLE books (
                 id INTEGER PRIMARY KEY,
                 user_id INTEGER,
                 title TEXT,
                 length TEXT,
                 difficulty TEXT,
                 genre TEXT,
                 format TEXT,
                 book_club BOOLEAN,
                 reread BOOLEAN,
                 points REAL,
                 FOREIGN KEY(user_id) REFERENCES users(id)
             )''')

c.execute('''CREATE TABLE user_genres (
                 user_id INTEGER,
                 genre TEXT,
                 FOREIGN KEY(user_id) REFERENCES users(id),
                 UNIQUE(user_id, genre)
             )''')

conn.commit()
conn.close()
