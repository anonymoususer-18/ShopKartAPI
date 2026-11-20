"""Unit tests: business rules only, no HTTP."""
import pytest

from shopkart.config import load_settings
from shopkart.exceptions import InvalidCoupon, OutOfStock
from shopkart.repository import Repository
from shopkart.schemas import CartRequest
from shopkart.services import CheckoutService


@pytest.fixture
def service():
    return CheckoutService(load_settings("development"), Repository())


def test_small_cart_pays_shipping(service):
    bill = service.quote(CartRequest(items=[{"product_id": 102, "quantity": 1}]))  # 499
    assert bill["subtotal"] == 499.0
    assert bill["gst"] == 89.82              # 18% of 499
    assert bill["shipping"] == 49            # below 999 -> pay shipping
    assert bill["total"] == 637.82


def test_big_cart_gets_free_shipping(service):
    bill = service.quote(CartRequest(items=[{"product_id": 101, "quantity": 2}]))  # 1598
    assert bill["shipping"] == 0


def test_fest20_coupon(service):
    cart = CartRequest(items=[{"product_id": 104, "quantity": 1}], coupon_code="fest20")
    bill = service.quote(cart)               # 1999, coupon code is case-insensitive
    assert bill["discount"] == 399.8


def test_coupon_needs_minimum_cart(service):
    cart = CartRequest(items=[{"product_id": 102, "quantity": 1}], coupon_code="FEST20")
    with pytest.raises(InvalidCoupon):
        service.quote(cart)


def test_out_of_stock(service):
    with pytest.raises(OutOfStock):
        service.quote(CartRequest(items=[{"product_id": 103, "quantity": 1}]))
