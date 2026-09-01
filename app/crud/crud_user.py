from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import StoreOwner
from app.schemas.user import UserCreate


async def get_user_by_email(db: AsyncSession, email: str) -> StoreOwner | None:
    result = await db.execute(select(StoreOwner).where(StoreOwner.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> StoreOwner:
    user = StoreOwner(email=user_in.email, hashed_password=hash_password(user_in.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
