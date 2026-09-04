import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: Decimal = Field(gt=0, decimal_places=3)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=255)
    customer_phone: str = Field(min_length=1, max_length=50)
    customer_address: str = Field(min_length=1, max_length=1000)
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    quantity: Decimal
    price_at_purchase: Decimal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    store_id: uuid.UUID
    customer_id: uuid.UUID
    customer_name: str
    customer_phone: str
    customer_address: str
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    items: list[OrderItemRead]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
