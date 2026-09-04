import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate


async def list_orders(db: AsyncSession, store_id: uuid.UUID) -> list[Order]:
    result = await db.execute(
        select(Order)
        .where(Order.store_id == store_id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


async def get_order(db: AsyncSession, store_id: uuid.UUID, order_id: uuid.UUID) -> Order | None:
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id, Order.store_id == store_id)
        .options(selectinload(Order.items))
    )
    return result.scalar_one_or_none()


async def list_orders_by_customer(db: AsyncSession, customer_id: uuid.UUID) -> list[Order]:
    result = await db.execute(
        select(Order)
        .where(Order.customer_id == customer_id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


async def create_order(
    db: AsyncSession, store_id: uuid.UUID, customer_id: uuid.UUID, order_in: OrderCreate
) -> Order:
    """Places an order, decrementing stock atomically under row locks to prevent overselling
    when multiple customers order the same product concurrently."""
    total_amount = Decimal("0")
    order_items: list[OrderItem] = []

    # Lock product rows in a stable order (by id) to avoid deadlocks between concurrent orders.
    product_ids = sorted({item.product_id for item in order_in.items}, key=str)
    result = await db.execute(
        select(Product)
        .where(Product.id.in_(product_ids), Product.store_id == store_id)
        .with_for_update()
    )
    products_by_id = {product.id: product for product in result.scalars().all()}

    for item in order_in.items:
        product = products_by_id.get(item.product_id)
        if product is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Product {item.product_id} not found in this store")
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Insufficient stock for '{product.name}': requested {item.quantity}, available {product.stock_quantity}",
            )
        product.stock_quantity -= item.quantity
        total_amount += product.price * item.quantity
        order_items.append(
            OrderItem(product_id=product.id, quantity=item.quantity, price_at_purchase=product.price)
        )

    order = Order(
        store_id=store_id,
        customer_id=customer_id,
        customer_name=order_in.customer_name,
        customer_phone=order_in.customer_phone,
        customer_address=order_in.customer_address,
        status=OrderStatus.PENDING,
        total_amount=total_amount,
        items=order_items,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order, attribute_names=["items"])
    return order


async def update_order_status(db: AsyncSession, order: Order, new_status: OrderStatus) -> Order:
    order.status = new_status
    await db.commit()
    await db.refresh(order)
    return order
