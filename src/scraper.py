import logging
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
