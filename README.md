# store-management

Multi-tenant store & stock management backend. Store owners manage products/stock under their own store URL; customers browse a store's public URL and place orders (COD/manual payment).

**Stack:** FastAPI + async SQLAlchemy 2.0 + PostgreSQL, JWT auth, Alembic migrations.

## Prerequisites

- Python 3.11+ (tested on 3.14)
- A PostgreSQL database (e.g. free tier on [Neon](https://neon.tech) or [Supabase](https://supabase.com))

## Setup

```bash
# 1. Clone and enter the repo
git clone git@github.com:Aakash4447/store-management-fast-api.git
cd store-management-fast-api

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# then edit .env:
#   DATABASE_URL   - your Postgres connection string (postgresql+asyncpg://...)
#   SECRET_KEY     - a long random string (e.g. `openssl rand -hex 32`)
```

## Run database migrations

```bash
# Generate the initial migration from the models (only needed once, or after model changes)
alembic revision --autogenerate -m "init"

# Apply migrations to the database
alembic upgrade head
```

## Start the server

```bash
uvicorn app.main:app --reload
```

- API base URL: `http://localhost:8000`
- Interactive docs (Swagger UI): `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Typical flow

1. `POST /api/v1/auth/register` — create a store-owner account
2. `POST /api/v1/auth/login` — get a JWT (`access_token`)
3. `POST /api/v1/stores` (authenticated) — create a store with a unique `slug`
4. `POST /api/v1/stores/{slug}/products` (authenticated) — add products with stock
5. Share `/{slug}` with customers — they can browse and order without an account:
   - `GET /api/v1/stores/{slug}/products` — public product listing
   - `POST /api/v1/stores/{slug}/orders` — place an order (stock is checked and decremented atomically)
6. `GET /api/v1/stores/{slug}/orders` / `PATCH /api/v1/stores/{slug}/orders/{order_id}` (authenticated) — manage incoming orders

## Project structure

```
app/
  api/v1/       # route handlers (auth, stores, products, orders)
  core/         # config and security (JWT, password hashing)
  crud/         # database operations
  db/           # engine/session setup
  models/       # SQLAlchemy models
  schemas/      # Pydantic request/response schemas
alembic/        # database migrations
```
