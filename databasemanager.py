from sqlalchemy import create_engine, Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime



Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    url = Column(String, primary_key=True)
    prices = relationship(
        "PriceHistory", back_populates="product", cascade="all, delete-orphan"
    )


class PriceHistory(Base):
    __tablename__ = "price_histories"

    id = Column(String, primary_key=True)
    product_url = Column(String, ForeignKey("products.url"))
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    main_image_url = Column(String)
    timestamp = Column(DateTime, nullable=False)
    product = relationship("Product", back_populates="prices")

class Database:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
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
print("DATABASE FILE LOADED:", __file__)
print("Database methods:", [m for m in dir(Database) if not m.startswith("_")])