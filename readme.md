# Automated Price Tracker

A Streamlit app that tracks product prices over time using Firecrawl for scraping and PostgreSQL for storage.
Click here to try the application : https://dhrupadraj-automated-price-tracker-ui-foqr7u.streamlit.app/

## Features
- Add product URLs from the UI.
- Scrape product name, price, currency, and image.
- Store historical prices in PostgreSQL.
- Visualize price trends with Plotly.

## Tech Stack
- Python
- Streamlit
- SQLAlchemy + psycopg2
- Firecrawl
- PostgreSQL (Supabase supported)

## Project Structure
- `ui.py`: Streamlit dashboard and user flow.
- `scraper.py`: Firecrawl-based product scraping.
- `databasemanager.py`: SQLAlchemy models and database access.
- `check_prices.py`: Batch updater script for tracked products.
- `utils.py`: URL validation helper(s).

## Requirements
- Python 3.9+
- A PostgreSQL database
- A Firecrawl API key

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables (Local)
Create a `.env` file:

```env
FIRECRAWL_API_KEY="your_firecrawl_api_key"
POSTGRES_URL="postgresql://username:password@host:5432/database?sslmode=require"
```

Notes:
- Keep `.env` out of git.
- For Supabase pooler, use port `6543` and keep `sslmode=require`.
- Do not add `pgbouncer=true` to this app's SQLAlchemy/psycopg2 URL.

## Run Locally
```bash
streamlit run ui.py
```

## Streamlit Cloud Setup
In app settings, add secrets in TOML format:

```toml
FIRECRAWL_API_KEY = "your_firecrawl_api_key"
POSTGRES_URL = "postgresql://username:password@host:6543/postgres?sslmode=require"
```

Then reboot/redeploy the app.

## Optional: Background Price Check
Run the batch script to update all tracked products:

```bash
python3 check_prices.py
```

## Common Errors
- `FIRECRAWL_API_KEY is missing`:
  - Add `FIRECRAWL_API_KEY` in `.env` (local) or Streamlit secrets (cloud).
- `invalid dsn: invalid connection option "pgbouncer"`:
  - Remove `pgbouncer=true` from `POSTGRES_URL`.
- `database "postgres sslmode=require" does not exist`:
  - URL formatting is wrong. Ensure `?sslmode=require` is appended with `?`, not space.
- `OperationalError` on cloud:
  - Verify host, port, username, password, and `sslmode=require`.
  - Confirm app is deployed from the latest commit.

## Security
- Never commit real credentials.
- Rotate keys/passwords immediately if they were exposed.
