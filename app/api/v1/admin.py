from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.crud.crud_store import list_all_stores
from app.crud.crud_user import list_users
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.store import StoreRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stores", response_model=list[StoreRead])
async def list_stores(_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await list_all_stores(db)


@router.get("/users", response_model=list[UserRead])
async def list_all_users(
    role: UserRole | None = None,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await list_users(db, role=role)
