import re
import pandas as pd
from typing import List, Dict, Any

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Zero": 0}

def clean_and_normalize(raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
    cleaned_rows = []
    for item in raw_data:
        price_match = re.search(r"\d+\.\d+", item.get("raw_price", ""))
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
