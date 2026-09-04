from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_customer, get_current_user
from app.crud.crud_order import list_orders_by_customer
from app.db.session import get_db
from app.models.user import User
from app.schemas.order import OrderRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=UserRead)
async def get_me(user: User = Depends(get_current_user)):
    return user


@router.get("/orders", response_model=list[OrderRead])
async def list_my_orders(customer: User = Depends(get_current_customer), db: AsyncSession = Depends(get_db)):
    return await list_orders_by_customer(db, customer.id)
