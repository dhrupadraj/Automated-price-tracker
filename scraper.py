import os
from firecrawl import Firecrawl
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()

firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
if not firecrawl_api_key:
    raise ValueError("FIRECRAWL_API_KEY is missing in environment variables.")

app = Firecrawl(firecrawl_api_key)

class Product(BaseModel):
    """Schema for creating a new product"""

    url: str = Field(description="The URL of the product")
    name: str = Field(description="The product name/title")
    price: float = Field(description="The current price of the product")
    currency: str = Field(description="Currency code (USD, EUR, etc)")
    main_image_url: str = Field(description="The URL of the main image of the product")


def scrape_product(url: str):
    data = app.scrape(url, formats=["markdown"])
    md = data.markdown or ""

    # ---- TITLE ----
    name = md.split("\n")[0].replace("#", "").strip() or "Unknown Product"

    # ---- PRICE ----
    price_match = re.search(r"\$([\d,]+\.?\d*)", md)
    price = float(price_match.group(1).replace(",", "")) if price_match else 0.0

    # ---- IMAGE ----
    img_match = re.search(r"!\[.*?\]\((https?://.*?)\)", md)
    main_image_url = img_match.group(1) if img_match else ""

    return {
        "url": url,
        "name": name,
        "price": price,
        "currency": "USD",
        "main_image_url": main_image_url,
        "timestamp": datetime.utcnow(),
    }

if __name__ == "__main__":
    product = "https://www.amazon.com/gp/product/B002U21ZZK/"

    print(scrape_product(product))
