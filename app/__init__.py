from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from app.settings.settings import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
session_local = async_sessionmaker(engine, expire_on_commit=False)
