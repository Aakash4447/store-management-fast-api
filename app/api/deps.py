from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.crud.crud_store import get_store_by_slug
from app.crud.crud_user import get_user_by_email
from app.db.session import get_db
from app.models.store import Store
from app.models.user import StoreOwner

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_owner(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> StoreOwner:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = decode_access_token(token)
    if email is None:
        raise credentials_error
    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_error
    return user


async def get_current_store(slug: str, db: AsyncSession = Depends(get_db)) -> Store:
    store = await get_store_by_slug(db, slug)
    if store is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Store not found")
    return store


async def verify_store_owner(
    store: Store = Depends(get_current_store),
    owner: StoreOwner = Depends(get_current_owner),
) -> Store:
    if store.owner_id != owner.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not own this store")
    return store
