import io
import logging
from http import HTTPStatus
from typing import List

import numpy as np
from fastapi import (
    FastAPI,
    Request,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import JSONResponse
from PIL import Image
from sqlalchemy import select
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app import session_local
from app.db_model.database import RequestHistory
from app.models import models
from app.settings.settings import ROOT_DIR

app = FastAPI()

templates = Jinja2Templates(directory=ROOT_DIR.as_posix() + "/app/templates/")
# Инициализация логирования
logging.basicConfig(level=logging.INFO)


async def process_image(image_bytes: bytes, model_name: str, length: int):
    """Обрабатывает изображение, приводит к необходимому формату,
     генерирует и возвращает описание.

    :param image_bytes: Изображение в байтовом формате
    :param model_name: Наименование модели
    :param length: Длина описания изображения
    :return:
    """
    # Преобразуем байты в изображение
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Преобразуем изображение в необходимые форматы для модели
    processed_image = np.array(image)

    # Получаем модель по имени
    model = models.available_models.get(model_name)
    if model is None:
        raise ValueError(f"Model {model_name} not found")

    # Генерация описания изображения
    description = await model.generate_description(processed_image, length)

    return description


async def save_image_description(description: str):
    """Сохраняет историю запроса

    :param description: описание изображения
    """
    async with session_local() as db_session:
        req = RequestHistory(image_description=description)
        db_session.add(req)
        await db_session.commit()


async def describe_image(file: UploadFile, model_name: str, length: int):
    contents = await file.read()
    description = await process_image(contents, model_name, length)
    await save_image_description(description)
    return description


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html",
    )


@app.post("/upload-image/")
async def upload_image(
        file: UploadFile = File(...),
        model_name: str = "blip",
        length: int = 20,
):
    """Получает файл изображения и возвращает его описание

    :param file: Файл изображения
    :param model_name: Наименование модели
    :param length: Длина описания изображения
    :return: Описание изображения
    :raise: HTTPException
    """
    if model_name not in models.available_models:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Model not found",
        )
    try:
        description = await describe_image(file, model_name, length)
        return {"description": description}
    except Exception as e:
        logging.error(f"Error during processing: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Processing error",
        )


@app.get("/history/", response_class=HTMLResponse)
async def get_history(request: Request):
    """Получает и возвращает список записей запросов с их идентификатором
    и описанием изображения

    :return: Список записей запросов с их идентификатором и
    описанием изображения
    """
    async with session_local() as db_session:
        query = select(RequestHistory)
        result = await db_session.execute(query)
        history = result.scalars().all()
    return templates.TemplateResponse(
        request=request, name="history.html", context={"history": history}
    )


@app.post("/upload-images/")
async def upload_images(
        files: List[UploadFile] = File(...),
        model_name: str = "blip",
        length: int = 20,
):
    if model_name not in models.available_models:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Model not found",
        )
    descriptions = []

    for file in files:
        try:
            # Логика обработки каждого файла
            descriptions.append(describe_image(file, model_name, length))
        except Exception as e:
            logging.error(
                f"Error: {e} during processing image: {file.filename}"
            )
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Error during processing image: {file.filename}"
            )

    return JSONResponse(content={"descriptions": descriptions})
