from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_store, get_current_store_owner
from app.crud.crud_store import create_store, list_stores_by_owner
from app.db.session import get_db
from app.models.store import Store
from app.models.user import User
from app.schemas.store import StoreCreate, StoreRead

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post("", response_model=StoreRead, status_code=201)
async def create_my_store(
    store_in: StoreCreate,
    owner: User = Depends(get_current_store_owner),
    db: AsyncSession = Depends(get_db),
):
    return await create_store(db, owner.id, store_in)


@router.get("/mine", response_model=list[StoreRead])
async def list_my_stores(
    owner: User = Depends(get_current_store_owner),
    db: AsyncSession = Depends(get_db),
):
    return await list_stores_by_owner(db, owner.id)


@router.get("/{slug}", response_model=StoreRead)
async def get_store(store: Store = Depends(get_current_store)):
    return store
