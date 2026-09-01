import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.store import Store
from app.schemas.store import StoreCreate


async def get_store_by_slug(db: AsyncSession, slug: str) -> Store | None:
    result = await db.execute(select(Store).where(Store.slug == slug))
    return result.scalar_one_or_none()


async def create_store(db: AsyncSession, owner_id: uuid.UUID, store_in: StoreCreate) -> Store:
    store = Store(name=store_in.name, slug=store_in.slug, owner_id=owner_id)
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return store
