import psycopg2
from psycopg2 import sql


def init_db():
    conn = psycopg2.connect(
        dbname="messenger",
        user="postgres",
        password="1111",
        host="localhost"
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