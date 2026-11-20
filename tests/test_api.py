"""API tests: send real HTTP-like requests with Flask's test client."""


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "UP"


def test_list_products_by_category(client):
    data = client.get("/api/v1/products?category=electronics").get_json()
    assert data["count"] == 2


def test_unknown_product_is_404(client):
    resp = client.get("/api/v1/products/999")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "product_not_found"


def test_create_product(client):
    resp = client.post("/api/v1/products",
                       json={"name": "LED Lamp", "price": 1249, "stock": 15, "category": "home"})
    assert resp.status_code == 201
    assert resp.get_json()["id"] == 106


def test_invalid_product_is_422(client):
    resp = client.post("/api/v1/products", json={"name": "TV", "price": -1})
    assert resp.status_code == 422
    fields = [d["field"] for d in resp.get_json()["details"]]
    assert "price" in fields and "category" in fields


def test_place_order_reduces_stock(client, valid_order):
    resp = client.post("/api/v1/orders", json=valid_order)
    assert resp.status_code == 201
    order = resp.get_json()
    assert order["status"] == "PLACED"
    assert order["total"] == 1885.64         # 1598 + 18% GST, free shipping
    assert client.get("/api/v1/products/101").get_json()["stock"] == 48

    # and we can fetch it back
    assert client.get(f"/api/v1/orders/{order['order_id']}").status_code == 200


def test_order_more_than_stock_is_409(client, valid_order):
    valid_order["items"] = [{"product_id": 104, "quantity": 5}]   # only 4 earbuds
    resp = client.post("/api/v1/orders", json=valid_order)
    assert resp.status_code == 409


def test_bad_pincode_is_422(client, valid_order):
    valid_order["address"]["pincode"] = "0123"
    resp = client.post("/api/v1/orders", json=valid_order)
    assert resp.status_code == 422
    assert resp.get_json()["details"][0]["field"] == "address.pincode"
