from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.crud.crud_user import create_user, get_user_by_email
from app.db.session import get_db
from app.models.user import UserRole
from app.schemas.user import Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_store_owner(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    return await create_user(db, user_in, role=UserRole.STORE_OWNER)


@router.post("/register/customer", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_customer(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    return await create_user(db, user_in, role=UserRole.CUSTOMER)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    return Token(access_token=create_access_token(subject=user.email), role=user.role)
