import os
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from databasemanager import Database
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from utils import is_valid_url
from scraper import scrape_product

load_dotenv()


def get_secret_value(key: str):
    env_value = os.getenv(key)
    if env_value:
        return env_value
    return st.secrets.get(key)


def _sanitize_error_message(message: str) -> str:
    # Redact credential fragments from URLs before showing errors in UI.
    return re.sub(r"://([^:@/]+):([^@/]+)@", r"://\1:***@", message)


postgres_url = get_secret_value("POSTGRES_URL")
if not postgres_url:
    st.error("POSTGRES_URL is missing. Add it to Streamlit secrets or environment variables.")
    st.stop()

with st.spinner("Loading database..."):
    try:
        db = Database(postgres_url)
    except OperationalError as e:
        detail = _sanitize_error_message(str(getattr(e, "orig", e)))
        st.error("Database connection failed. Check POSTGRES_URL credentials, host, and sslmode.")
        st.code(detail)
        st.stop()
    except SQLAlchemyError as e:
        detail = _sanitize_error_message(str(e))
        st.error("Database setup failed with SQLAlchemy error.")
        st.code(detail)
        st.stop()
    except ValueError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        detail = _sanitize_error_message(str(e))
        st.error("Database initialization failed. Check Streamlit logs for the exact connection error.")
        st.code(detail if detail else repr(e))
        st.stop()


# Set up sidebar
with st.sidebar:
    st.title("Add New Product")
    product_url = st.text_input("Product URL")
    add_button = st.button("Add Product")

    if add_button:
        if not product_url:
            st.error("Please enter a product URL")
        elif not is_valid_url(product_url):
            st.error("Please enter a valid URL")
        else:
            db.add_product(product_url)  # This is the new line
            with st.spinner("Added product to database. Scraping product data..."):
                try:
                    product_data = scrape_product(product_url)
                    db.add_price(product_data)
                except ValueError as e:
                    st.error(str(e))
                except Exception:
                    st.error("Failed to scrape product data. Please try again.")
                else:
                    st.success("Product is now being tracked!")

# Main content
st.title("Price Tracker Dashboard")
st.markdown("## Tracked Products")

# Get all products
products = db.get_all_products()

# Create a card for each product
for product in products:
    price_history = db.get_price_history(product.url)
    if price_history:
        # Create DataFrame for plotting
        df = pd.DataFrame(
            [
                {"timestamp": ph.timestamp, "price": ph.price, "name": ph.name}
                for ph in price_history
            ]
        )

        # Create a card-like container for each product
        with st.expander(df["name"][0], expanded=False):
            st.markdown("---")
            col1, col2 = st.columns([1, 3])

            with col1:
                if price_history[0].main_image_url:
                    st.image(price_history[0].main_image_url, width=200)
                st.metric(
                    label="Current Price",
                    value=f"{price_history[0].price} {price_history[0].currency}",
                )
            with col2:
                # Create price history plot
                fig = px.line(
                    df,
                    x="timestamp",
                    y="price",
                    title=None,
                )
                fig.update_layout(
                    xaxis_title=None,
                    yaxis_title="Price",
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=300,
                )
                fig.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=45)
                fig.update_yaxes(tickprefix=f"{price_history[0].currency} ", tickformat=".2f")
                st.plotly_chart(fig, use_container_width=True)
