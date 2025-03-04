import asyncio

import uvicorn

from app import DbInterface, engine, session_local
from app.api.route import app
from app.settings.settings import FASTAPI_HOST, FASTAPI_PORT

if __name__ == '__main__':
    ydb = DbInterface(engine, session_local)
    asyncio.run(ydb.create_all())

    uvicorn.run(
        'main:app',
        host=FASTAPI_HOST,
        port=FASTAPI_PORT,
        reload=True,
    )
