import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_store, verify_store_owner
from app.crud.crud_product import (
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)
from app.db.session import get_db
from app.models.store import Store
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/stores/{slug}/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
async def list_store_products(store: Store = Depends(get_current_store), db: AsyncSession = Depends(get_db)):
    return await list_products(db, store.id)


@router.get("/{product_id}", response_model=ProductRead)
async def get_store_product(
    product_id: uuid.UUID, store: Store = Depends(get_current_store), db: AsyncSession = Depends(get_db)
):
    product = await get_product(db, store.id, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return product


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_store_product(
    product_in: ProductCreate,
    store: Store = Depends(verify_store_owner),
    db: AsyncSession = Depends(get_db),
):
    return await create_product(db, store.id, product_in)


@router.put("/{product_id}", response_model=ProductRead)
async def update_store_product(
    product_id: uuid.UUID,
    product_in: ProductUpdate,
    store: Store = Depends(verify_store_owner),
    db: AsyncSession = Depends(get_db),
):
    product = await get_product(db, store.id, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return await update_product(db, product, product_in)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store_product(
    product_id: uuid.UUID,
    store: Store = Depends(verify_store_owner),
    db: AsyncSession = Depends(get_db),
):
    product = await get_product(db, store.id, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    await delete_product(db, product)
