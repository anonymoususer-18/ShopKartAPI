"""Business logic layer: prices, coupons, GST, shipping, stock rules.
No Flask code here -> easy to test and reuse (e.g. from a CLI or a queue worker)."""
import logging
from datetime import datetime

from .exceptions import InvalidCoupon, OutOfStock, ShopKartError

logger = logging.getLogger("shopkart.services")


class CheckoutService:
    def __init__(self, settings, repo):
        self.store = settings.store
        self.coupons = {c.code: c for c in settings.coupons}
        self.repo = repo
        self._next_order_number = 1001

    def quote(self, cart):
        """Price breakdown for a cart. Does NOT change stock."""
        lines, subtotal = [], 0.0
        for item in cart.items:
            if item.quantity > self.store.max_qty_per_item:
                raise ShopKartError(f"Max {self.store.max_qty_per_item} units per product")
            product = self.repo.get_product(item.product_id)
            if product["stock"] < item.quantity:
                raise OutOfStock(f"{product['name']}: only {product['stock']} left")
            line_total = round(product["price"] * item.quantity, 2)
            subtotal += line_total
            lines.append({"product_id": product["id"], "name": product["name"],
                          "unit_price": product["price"], "quantity": item.quantity,
                          "line_total": line_total})

        discount = self._discount(subtotal, cart.coupon_code)
        after_discount = subtotal - discount
        gst = round(after_discount * self.store.gst_percent / 100, 2)
        shipping = 0 if after_discount >= self.store.free_shipping_above else self.store.shipping_fee
        return {
            "lines": lines,
            "subtotal": round(subtotal, 2),
            "coupon_code": cart.coupon_code,
            "discount": discount,
            "gst": gst,
            "shipping": shipping,
            "total": round(after_discount + gst + shipping, 2),
            "currency": self.store.currency,
        }

    def _discount(self, subtotal, code):
        if not code:
            return 0.0
        coupon = self.coupons.get(code.upper())
        if coupon is None:
            raise InvalidCoupon(f"Coupon '{code}' is invalid or expired")
        if subtotal < coupon.min_cart_value:
            raise InvalidCoupon(f"{coupon.code} needs a cart of Rs.{coupon.min_cart_value:.0f} or more")
        return round(subtotal * coupon.discount_percent / 100, 2)

    def place_order(self, order_request):
        bill = self.quote(order_request)               # checks stock for ALL items first
        for line in bill["lines"]:                     # only then reduce stock
            self.repo.reduce_stock(line["product_id"], line["quantity"])

        order_id = f"SK-{self._next_order_number}"
        self._next_order_number += 1
        order = {
            "order_id": order_id,
            "status": "PLACED",
            "customer_email": order_request.customer_email,
            "address": order_request.address.model_dump(),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            **bill,
        }
        self.repo.save_order(order)
        logger.info("Order %s placed: %d lines, total Rs.%.2f",
                    order_id, len(bill["lines"]), bill["total"])
        return order
