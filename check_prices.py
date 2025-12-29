import os
from databasemanager import Database
from dotenv import load_dotenv
from firecrawl import Firecrawl
from scraper import scrape_product

load_dotenv()

db = Database(os.getenv("POSTGRES_URL"))
app = Firecrawl()

def check_prices():
    products = db.get_all_products()

    for product in products:
        try:
            updated_product = scrape_product(product.url)
            db.add_price(updated_product)
            print(f"Added new price entry for {updated_product['name']}")
        except Exception as e:
            print(f"Error processing {product.url}: {e}")


if __name__ == "__main__":
    check_prices()