"""HTTP layer: URLs -> call the service -> return JSON.  Kept thin on purpose."""
import logging

from flask import Blueprint, current_app, jsonify, request

from .schemas import CartRequest, OrderRequest, ProductCreate

logger = logging.getLogger("shopkart.api")
api = Blueprint("api", __name__, url_prefix="/api/v1")    # versioned API


def _service():
    return current_app.extensions["checkout_service"]


def _repo():
    return current_app.extensions["repository"]


def _json_body():
    return request.get_json(silent=True) or {}


@api.get("/products")
def list_products():
    items = _repo().list_products(category=request.args.get("category"))
    return jsonify(count=len(items), items=items)


@api.get("/products/<int:product_id>")
def get_product(product_id):
    return jsonify(_repo().get_product(product_id))


@api.post("/products")
def create_product():
    data = ProductCreate.model_validate(_json_body())
    product = _repo().add_product(data.model_dump())
    logger.info("Product %s created: %s", product["id"], product["name"])
    return jsonify(product), 201


@api.post("/cart/quote")
def cart_quote():
    cart = CartRequest.model_validate(_json_body())
    return jsonify(_service().quote(cart))


@api.post("/orders")
def place_order():
    order_request = OrderRequest.model_validate(_json_body())
    order = _service().place_order(order_request)
    return jsonify(order), 201


@api.get("/orders/<order_id>")
def get_order(order_id):
    return jsonify(_repo().get_order(order_id))
