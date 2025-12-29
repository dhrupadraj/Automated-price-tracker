import os
from firecrawl import Firecrawl
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from bs4 import BeautifulSoup
#from IPython.display import Markdown
from datetime import datetime

load_dotenv()

app = Firecrawl(os.getenv("FIRECRAWL_API_KEY"))

class Product(BaseModel):
    """Schema for creating a new product"""

    url: str = Field(description="The URL of the product")
    name: str = Field(description="The product name/title")
    price: float = Field(description="The current price of the product")
    currency: str = Field(description="Currency code (USD, EUR, etc)")
    main_image_url: str = Field(description="The URL of the main image of the product")
 
  
def scrape_product(url: str):
    # Scrape the page as Markdown
    data = app.scrape(url, formats=["markdown"])

    # Get the Markdown text (not data.content)
    markdown_content = data.markdown

    # Parse with BeautifulSoup (works for Markdown too, since it's mostly HTML)
    soup = BeautifulSoup(markdown_content, "html.parser")

    # Extract product info (example for Amazon)
    title_tag = soup.find("span", {"id": "productTitle"})
    name = title_tag.get_text(strip=True) if title_tag else "N/A"

    price_tag = soup.find("span", {"id": "priceblock_ourprice"})
    price_text = price_tag.get_text(strip=True) if price_tag else "0"
    try:
        price = float(price_text.replace("$", "").replace(",", ""))
    except ValueError:
        price = 0.0

    img_tag = soup.find("img", {"id": "landingImage"})
    main_image_url = img_tag["src"] if img_tag else ""

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
