import psycopg2
import os
from urllib.parse import urlparse

def init_db():
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL is None:
        raise ValueError("DATABASE_URL environment variable is not set")

    result = urlparse(DATABASE_URL)

    conn = psycopg2.connect(
        dbname=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

    cur = conn.cursor()

    # Створення таблиць
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        phone VARCHAR(20) UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        sender_id INTEGER REFERENCES users(id),
        receiver_id INTEGER REFERENCES users(id),
        text TEXT,
        timestamp TIMESTAMP DEFAULT NOW()
    )
    """)

    conn.commit()
    return conn
