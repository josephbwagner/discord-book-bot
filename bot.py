import discord
from discord.ext import commands
import sqlite3


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

BOOK_LENGTH_POINTS = {"short": 0.5, "medium": 1, "long": 1.5}
DIFFICULTY_POINTS = {"light": 0.5, "moderate": 1, "challenging": 1.5}
FORMAT_POINTS = {"print": 1, "ebook": 0.5, "audiobook": 0.5}
BONUS_POINTS = 1
BOOK_CLUB_POINTS = 0.5
REREAD_POINTS = 0.5

def get_user_id(conn, discord_id):
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE discord_id = ?', (discord_id,))
    result = c.fetchone()
    if result:
        return result[0]
    c.execute('INSERT INTO users (discord_id) VALUES (?)', (discord_id,))
    conn.commit()
    return c.lastrowid

def add_book(conn, user_id, title, length, difficulty, genre, format, book_club, reread, points):
    c = conn.cursor()
    c.execute('''INSERT INTO books (user_id, title, length, difficulty, genre, format, book_club, reread, points)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, title, length, difficulty, genre, format, book_club, reread, points))
    c.execute('''INSERT OR IGNORE INTO user_genres (user_id, genre) VALUES (?, ?)''', (user_id, genre))
    conn.commit()

def get_user_points(conn, user_id):
    c = conn.cursor()
    c.execute('SELECT points FROM books WHERE user_id = ?', (user_id,))
    return sum(row[0] for row in c.fetchall())

def get_user_genres(conn, user_id):
    c = conn.cursor()
    c.execute('SELECT COUNT(DISTINCT genre) FROM user_genres WHERE user_id = ?', (user_id,))
    return c.fetchone()[0]

def get_leaderboard(conn):
    c = conn.cursor()
    c.execute('''SELECT discord_id, (SELECT SUM(points) FROM books WHERE user_id = users.id) + 
                 (SELECT COUNT(DISTINCT genre) * ? FROM user_genres WHERE user_id = users.id) as total_points
                 FROM users
                 ORDER BY total_points DESC''', (BONUS_POINTS,))
    return c.fetchall()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='logbook')
async def log_book(ctx, title, length, difficulty, genre, format, book_club: bool = False, reread: bool = False):
    conn = sqlite3.connect('books.db')
    user_id = get_user_id(conn, str(ctx.author))
    
    points = (BOOK_LENGTH_POINTS[length] + 
              DIFFICULTY_POINTS[difficulty] + 
              FORMAT_POINTS[format] +
              (BOOK_CLUB_POINTS if book_club else 0) +
              (REREAD_POINTS if reread else 0))

    add_book(conn, user_id, title, length, difficulty, genre, format, book_club, reread, points)
    
    total_points = get_user_points(conn, user_id)
    conn.close()
    
    await ctx.send(f'Logged {title} for {ctx.author}. Total points: {total_points:.2f}')

@bot.command(name='score')
async def score(ctx):
    conn = sqlite3.connect('books.db')
    user_id = get_user_id(conn, str(ctx.author))
    total_points = get_user_points(conn, user_id) + (BONUS_POINTS * get_user_genres(conn, user_id))
    conn.close()
    
    await ctx.send(f'{ctx.author}, your total points are: {total_points:.2f}')

@bot.command(name='leaderboard')
async def leaderboard(ctx):
    conn = sqlite3.connect('books.db')
    leaderboard = get_leaderboard(conn)
    conn.close()
    
    message = "Leaderboard:\n"
    for i, (discord_id, total_points) in enumerate(leaderboard, start=1):
        message += f"{i}. {discord_id}: {total_points:.2f} points\n"
    await ctx.send(message)

bot.run('YOUR_BOT_TOKEN')
