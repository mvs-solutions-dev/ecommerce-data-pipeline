import os
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
