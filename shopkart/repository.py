"""Data access layer. Today it keeps data in memory (loaded from a JSON file).
Tomorrow you can swap this file for a real database - routes and services stay the same."""
import json
import logging
from pathlib import Path

from .exceptions import OrderNotFound, ProductNotFound

logger = logging.getLogger("shopkart.repository")
DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"


class Repository:
    def __init__(self, data_file=DATA_FILE):
        with open(data_file, encoding="utf-8") as f:
            self.products = {p["id"]: p for p in json.load(f)}
        self.orders = {}
        logger.info("Loaded %d products from %s", len(self.products), Path(data_file).name)

    # ----- products -----
    def list_products(self, category=None):
        items = list(self.products.values())
        if category:
            items = [p for p in items if p["category"] == category]
        return items

    def get_product(self, product_id):
        if product_id not in self.products:
            raise ProductNotFound(f"Product {product_id} not found")
        return self.products[product_id]

    def add_product(self, data):
        new_id = max(self.products, default=100) + 1
        product = {"id": new_id, **data}
        self.products[new_id] = product
        return product

    def reduce_stock(self, product_id, quantity):
        self.get_product(product_id)["stock"] -= quantity

    # ----- orders -----
    def save_order(self, order):
        self.orders[order["order_id"]] = order
        return order

    def get_order(self, order_id):
        if order_id not in self.orders:
            raise OrderNotFound(f"Order {order_id} not found")
        return self.orders[order_id]
