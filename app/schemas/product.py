import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    sku: str | None = Field(default=None, max_length=100)
    price: Decimal = Field(gt=0)
    stock_quantity: int = Field(ge=0, default=0)
    image_url: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    sku: str | None = Field(default=None, max_length=100)
    price: Decimal | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    image_url: str | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    store_id: uuid.UUID
    name: str
    description: str | None
    sku: str | None
    price: Decimal
    stock_quantity: int
    image_url: str | None
    created_at: datetime
    updated_at: datetime
