import configparser
from pathlib import Path

ROOT_DIR = Path(__file__).parents[2]

config = configparser.ConfigParser()
config.read(ROOT_DIR / 'config.ini')

# настройки подключения к БД
postgres_settings = config['POSTGRES']
POSTGRES_USER = postgres_settings.get('USER', 'user')
POSTGRES_PASSWORD = postgres_settings.get('PASSWORD', 'password')
POSTGRES_HOST = postgres_settings.get('HOST', 'localhost')
POSTGRES_PORT = int(postgres_settings.get('PORT', '5432'))
POSTGRES_DATABASE = postgres_settings.get('DATABASE', 'dbname')
DATABASE_URL = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DATABASE}'

# настройки подключения FastAPI
fastapi_settings = config['FASTAPI']
FASTAPI_HOST = fastapi_settings.get('HOST', 'localhost')
FASTAPI_PORT = int(fastapi_settings.get('PORT', '5005'))
