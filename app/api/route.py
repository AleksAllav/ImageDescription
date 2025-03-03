from http import HTTPStatus
from typing import List

from fastapi import (
    UploadFile,
    File,
    HTTPException,
    FastAPI,
)
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.models import models
from app.db_model.database import RequestHistory
from app import session_local
import logging
import io
from PIL import Image
import numpy as np

app = FastAPI()

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
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Model not found")
    try:
        return {"description": describe_image(file, model_name, length)}
    except Exception as e:
        logging.error(f"Error during processing: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Processing error")


@app.get("/history/", response_model=None)
async def get_history():
    """Получает и возвращает список записей запросов с их идентификатором и описанием изображения

    :return: Список записей запросов с их идентификатором и описанием изображения
    """
    async with session_local() as db_session:
        query = select(RequestHistory)
        result = await db_session.execute(query)
        history = result.scalars().all()
    return [{"id": record.id, "description": record.image_description} for record in history]


@app.post("/upload-images/")
async def upload_images(
        files: List[UploadFile] = File(...),
        model_name: str = "blip",
        length: int = 20,
):
    if model_name not in models.available_models:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Model not found")
    descriptions = []

    for file in files:
        try:
            # Логика обработки каждого файла
            descriptions.append(describe_image(file, model_name, length))
        except Exception as e:
            logging.error(f"Error: {e} during processing image: {file.filename}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Error during processing image: {file.filename}"
            )

    return JSONResponse(content={"descriptions": descriptions})
