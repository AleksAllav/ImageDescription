import uvicorn

from app.api.route import app
from app.settings.settings import FASTAPI_HOST, FASTAPI_PORT

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=FASTAPI_HOST,
        port=FASTAPI_PORT,
        reload=True,
    )
