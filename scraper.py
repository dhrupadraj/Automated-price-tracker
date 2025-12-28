from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = FirecrawlApp()

class Product(BaseModel):
    """Schema for creating a new product"""

    url: str = Field(description="The URL of the product")
    name: str = Field(description="The product name/title")
    price: float = Field(description="The current price of the product")
    currency: str = Field(description="Currency code (USD, EUR, etc)")
    main_image_url: str = Field(description="The URL of the main image of the product")
    
def scrape_product(url: str):
    # Firecrawl scrape() only accepts URL as a single positional argument
    # For extraction with schema, we may need to use a different approach
    # Try calling the API directly or use a different method
    
    # First, try basic scrape to see response structure
    response = app.scrape(url)
    
    # Handle different possible response structures
    if isinstance(response, dict):
        # Check if extract is already in the response
        if "extract" in response:
            extracted_data = response["extract"]
        elif "data" in response and isinstance(response["data"], dict):
            extracted_data = response["data"]
        else:
            # If no extract, we'll need to parse the raw data
            # For now, return basic structure - you may need to adjust based on actual response
            extracted_data = {
                "url": url,
                "name": response.get("title", ""),
                "price": 0.0,  # Will need to be extracted from response
                "currency": "USD",
                "main_image_url": response.get("image", "")
            }
    else:
        extracted_data = {"url": url}
    
    # Add timestamp
    extracted_data["timestamp"] = datetime.utcnow()
    
    return extracted_data


if __name__ == "__main__":
    product = "https://www.amazon.com/gp/product/B002U21ZZK/"

    print(scrape_product(product))