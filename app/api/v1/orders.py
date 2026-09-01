import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_store, verify_store_owner
from app.crud.crud_order import create_order, get_order, list_orders, update_order_status
from app.db.session import get_db
from app.models.store import Store
from app.schemas.order import OrderCreate, OrderRead, OrderStatusUpdate

router = APIRouter(prefix="/stores/{slug}/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def place_order(
    order_in: OrderCreate, store: Store = Depends(get_current_store), db: AsyncSession = Depends(get_db)
):
    return await create_order(db, store.id, order_in)


@router.get("", response_model=list[OrderRead])
async def list_store_orders(store: Store = Depends(verify_store_owner), db: AsyncSession = Depends(get_db)):
    return await list_orders(db, store.id)


@router.patch("/{order_id}", response_model=OrderRead)
async def update_store_order_status(
    order_id: uuid.UUID,
    status_in: OrderStatusUpdate,
    store: Store = Depends(verify_store_owner),
    db: AsyncSession = Depends(get_db),
):
    order = await get_order(db, store.id, order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    return await update_order_status(db, order, status_in.status)
