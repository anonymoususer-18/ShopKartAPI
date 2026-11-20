"""Business errors. Each one knows its HTTP status code and a short error code,
so ONE error handler in routes.py can turn any of them into a clean JSON response."""


class ShopKartError(Exception):
    status_code = 400
    error_code = "shopkart_error"

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ProductNotFound(ShopKartError):
    status_code = 404
    error_code = "product_not_found"


class OrderNotFound(ShopKartError):
    status_code = 404
    error_code = "order_not_found"


class OutOfStock(ShopKartError):
    status_code = 409
    error_code = "out_of_stock"


class InvalidCoupon(ShopKartError):
    status_code = 400
    error_code = "invalid_coupon"
