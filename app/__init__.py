from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.db_model.database import Base
from app.settings.settings import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
session_local = async_sessionmaker(engine, expire_on_commit=False)


class DbInterface:
    def __init__(self, engine_, session):
        self.engine = engine_
        self.session = session

    async def create_db(self):
        async with self.engine.begin() as conn:
            if not database_exists(self.engine.url):
                await conn.run_sync(create_database(self.engine.url))

    async def drop_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(drop_database(self.engine.url))

    async def create_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
