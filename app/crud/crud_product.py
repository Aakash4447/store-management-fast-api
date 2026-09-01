import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


async def list_products(db: AsyncSession, store_id: uuid.UUID) -> list[Product]:
    result = await db.execute(select(Product).where(Product.store_id == store_id).order_by(Product.created_at))
    return list(result.scalars().all())


async def get_product(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID) -> Product | None:
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.store_id == store_id)
    )
    return result.scalar_one_or_none()


async def create_product(db: AsyncSession, store_id: uuid.UUID, product_in: ProductCreate) -> Product:
    product = Product(store_id=store_id, **product_in.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def update_product(db: AsyncSession, product: Product, product_in: ProductUpdate) -> Product:
    for field, value in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(db: AsyncSession, product: Product) -> None:
    await db.delete(product)
    await db.commit()
