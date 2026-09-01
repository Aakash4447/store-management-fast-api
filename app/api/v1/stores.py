from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_owner, get_current_store
from app.crud.crud_store import create_store
from app.db.session import get_db
from app.models.store import Store
from app.models.user import StoreOwner
from app.schemas.store import StoreCreate, StoreRead

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post("", response_model=StoreRead, status_code=201)
async def create_my_store(
    store_in: StoreCreate,
    owner: StoreOwner = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db),
):
    return await create_store(db, owner.id, store_in)


@router.get("/{slug}", response_model=StoreRead)
async def get_store(store: Store = Depends(get_current_store)):
    return store
