import os

print("Criando estrutura de pastas...")
os.makedirs("src", exist_ok=True)
os.makedirs("data", exist_ok=True)

# 1. requirements.txt
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write("requests>=2.31.0\nbeautifulsoup4>=4.12.0\npandas>=2.0.0\n")

# 2. .gitignore
with open(".gitignore", "w", encoding="utf-8") as f:
    f.write("__pycache__/\n*.py[cod]\n*$py.class\ndata/*.csv\ndata/*.sqlite\nvenv/\n.env\n")

# 3. README.md
readme = """# E-Commerce Automated Data Pipeline & Scraper (Python)

A robust Python data pipeline designed to extract, clean, and store structured product catalog data.

## Features
- Automated Web Scraping using Requests and BeautifulSoup4
- Data Normalization and Cleaning with Pandas
- Dual Export: Clean .csv file and structured SQLite database
- Error handling and logging

## Quick Start
1. Install dependencies:
   pip install -r requirements.txt
2. Run the pipeline:
   python main.py
"""
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

# 4. src/scraper.py
scraper = """import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_URL = "https://books.toscrape.com/"

def fetch_page_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text

def parse_catalog_page(html_content: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html_content, "html.parser")
    products = []
    cards = soup.find_all("article", class_="product_pod")
    for card in cards:
        title_tag = card.h3.find("a")
        title = title_tag.get("title", "").strip() if title_tag else "Unknown"
        relative_link = title_tag.get("href", "") if title_tag else ""
        product_url = BASE_URL + "catalogue/" + relative_link.replace("../", "")
        
        price_tag = card.find("p", class_="price_color")
        raw_price = price_tag.text.strip() if price_tag else "0.00"
        
        rating_tag = card.find("p", class_="star-rating")
        raw_rating = "Zero"
        if rating_tag:
            rating_classes = [c for c in rating_tag.get("class", []) if c != "star-rating"]
            if rating_classes:
                raw_rating = rating_classes[0]
                
        stock_tag = card.find("p", class_="instock availability")
        raw_stock = stock_tag.text.strip() if stock_tag else "Out of stock"
        
        products.append({
            "title": title,
            "product_url": product_url,
            "raw_price": raw_price,
            "raw_rating": raw_rating,
            "raw_stock": raw_stock
        })
    return products
"""
with open("src/scraper.py", "w", encoding="utf-8") as f:
    f.write(scraper)

# 5. src/parser.py
parser_code = """import re
import pandas as pd
from typing import List, Dict, Any

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Zero": 0}

def clean_and_normalize(raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
    cleaned_rows = []
    for item in raw_data:
        price_match = re.search(r"\\d+\\.\\d+", item.get("raw_price", ""))
        price = float(price_match.group(0)) if price_match else 0.0
        
        rating_str = item.get("raw_rating", "Zero")
        rating = RATING_MAP.get(rating_str, 0)
        
        stock_str = item.get("raw_stock", "").lower()
        in_stock = 1 if "in stock" in stock_str else 0
        
        cleaned_rows.append({
            "title": item.get("title"),
            "price_gbp": price,
            "rating_stars": rating,
            "in_stock": in_stock,
            "product_url": item.get("product_url")
        })
    return pd.DataFrame(cleaned_rows)
"""
with open("src/parser.py", "w", encoding="utf-8") as f:
    f.write(parser_code)

# 6. src/database.py
db_code = """import sqlite3
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
"""
with open("src/database.py", "w", encoding="utf-8") as f:
    f.write(db_code)

# 7. main.py
main_code = """import os
import logging
from src.scraper import fetch_page_html, parse_catalog_page, BASE_URL
from src.parser import clean_and_normalize
from src.database import store_in_sqlite

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run_pipeline():
    logging.info("Iniciando pipeline de extração e tratamento...")
    os.makedirs("data", exist_ok=True)
    
    html_content = fetch_page_html(BASE_URL)
    raw_products = parse_catalog_page(html_content)
    logging.info(f"Itens brutos extraidos: {len(raw_products)}")
    
    df = clean_and_normalize(raw_products)
    
    # Salva CSV
    csv_path = "data/output.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    logging.info(f"CSV exportado com sucesso: {csv_path}")
    
    # Salva SQLite
    db_path = "data/database.sqlite"
    store_in_sqlite(df, db_path)
    
    logging.info("Pipeline concluido com sucesso!")

if __name__ == "__main__":
    run_pipeline()
"""
with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)

print("=" * 50)
print("PROJETO GERADO COM SUCESSO!")
print("=" * 50)