import sqlite3
import pandas as pd
import logging

def store_in_sqlite(df: pd.DataFrame, db_path: str = "data/database.sqlite") -> None:
    logging.info(f"Conectando ao banco SQLite: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL,
            rating_stars INTEGER,
            in_stock INTEGER,
            product_url TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO products (title, price_gbp, rating_stars, in_stock, product_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (row["title"], row["price_gbp"], row["rating_stars"], row["in_stock"], row["product_url"]))
    conn.commit()
    conn.close()
    logging.info("Dados gravados com sucesso no banco de dados!")
