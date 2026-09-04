"""Create an admin user directly in the database.

Admin accounts are intentionally not self-registerable through the public API
(unlike store owners and customers) since they get platform-wide oversight.

Usage:
    python -m app.scripts.create_admin <email> <password>
"""
import asyncio
import sys

from app.core.security import hash_password
from app.crud.crud_user import get_user_by_email
from app.db.session import async_session_factory
from app.models import order, product, store  # noqa: F401 - registers models for relationship resolution
from app.models.user import User, UserRole


async def main(email: str, password: str) -> None:
    async with async_session_factory() as db:
        existing = await get_user_by_email(db, email)
        if existing:
            print(f"A user with email {email!r} already exists (role={existing.role.value}).")
            return
        user = User(email=email, hashed_password=hash_password(password), role=UserRole.ADMIN)
        db.add(user)
        await db.commit()
        print(f"Created admin user {email!r}.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m app.scripts.create_admin <email> <password>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
