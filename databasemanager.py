from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit



class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    url: Mapped[str] = mapped_column(String, primary_key=True)
    prices: Mapped[list["PriceHistory"]] = relationship(
        "PriceHistory", back_populates="product", cascade="all, delete-orphan"
    )


class PriceHistory(Base):
    __tablename__ = "price_histories"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_url: Mapped[str] = mapped_column(String, ForeignKey("products.url"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False)
    main_image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    product: Mapped[Product] = relationship("Product", back_populates="prices")


def _normalize_postgres_url(connection_string: str) -> str:
    normalized = connection_string.strip().strip("'").strip('"')
    if normalized.startswith("postgres://"):
        normalized = normalized.replace("postgres://", "postgresql://", 1)

    parsed = urlsplit(normalized)
    if not parsed.scheme or not parsed.hostname:
        raise ValueError("POSTGRES_URL is invalid: missing scheme or host")

    host = parsed.hostname
    if host is None:
        raise ValueError("POSTGRES_URL is invalid: could not parse host")

    host_part = host
    if parsed.port is not None:
        host_part = f"{host_part}:{parsed.port}"

    userinfo = ""
    if parsed.username is not None:
        username = quote(parsed.username, safe="")
        if parsed.password is not None:
            password = quote(parsed.password, safe="")
            userinfo = f"{username}:{password}@"
        else:
            userinfo = f"{username}@"

    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "supabase.co" in host and "sslmode" not in query_params:
        query_params["sslmode"] = "require"

    return urlunsplit(
        (parsed.scheme, f"{userinfo}{host_part}", parsed.path, urlencode(query_params), parsed.fragment)
    )


class Database:
    def __init__(self, connection_string):
        if not connection_string:
            raise ValueError("Connection string is required")

        normalized_connection_string = _normalize_postgres_url(connection_string)
        self.engine = create_engine(normalized_connection_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_product(self, url):
        session = self.Session()
        try:
            # Create the product entry
            product = Product(url=url)
            session.merge(product)  # merge will update if exists, insert if not
            session.commit()
        finally:
            session.close()

    def add_price(self, product_data):
        session = self.Session()
        try:
            price_history = PriceHistory(
                id=f"{product_data['url']}_{product_data['timestamp']}",
                product_url=product_data["url"],
                name=product_data["name"],
                price=product_data["price"],
                currency=product_data["currency"],
                main_image_url=product_data["main_image_url"],
                timestamp=product_data["timestamp"],
            )
            session.add(price_history)
            session.commit()
        finally:
            session.close()

    def get_price_history(self, url):
        """Get price history for a product"""
        session = self.Session()
        try:
            return (
                session.query(PriceHistory)
                .filter(PriceHistory.product_url == url)
                .order_by(PriceHistory.timestamp.desc())
                .all()
            )
        finally:
            session.close()

    def get_all_products(self):
        session = self.Session()
        try:
            return session.query(Product).all()
        finally:
            session.close()
