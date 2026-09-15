import os


class Config(object):
    """Конфигурация приложения Flask."""

    SECRET_KEY = os.getenv('SECRET_KEY')  # Ключ для защиты от CSRF.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI'
    )  # Строка подключения к базе данных.
    YANDEX_TOKEN = os.getenv('DISK_TOKEN')  # Токен для работы с Яндекс.Диском.
