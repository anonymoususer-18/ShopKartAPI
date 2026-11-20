"""Pydantic schemas = the 'contract' of our API (what comes in, what goes out)."""
from typing import List, Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    category: str = Field(min_length=2)


class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)


class Address(BaseModel):
    name: str = Field(min_length=2)
    city: str
    pincode: str = Field(pattern=r"^[1-9][0-9]{5}$")
    phone: str = Field(pattern=r"^[6-9][0-9]{9}$")


class CartRequest(BaseModel):
    items: List[CartItem] = Field(min_length=1)
    coupon_code: Optional[str] = None


class OrderRequest(CartRequest):          # an order = a cart + where to deliver
    customer_email: str = Field(pattern=r"^[\w.+-]+@[\w-]+\.[\w.]+$")
    address: Address
