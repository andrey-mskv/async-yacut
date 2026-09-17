from . import app

# import requests

import asyncio
import aiohttp

# import time

# import json

# from pprint import pprint
import urllib

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'

AUTH_HEADERS = {'Authorization': f"OAuth {app.config['DISK_TOKEN']}"}

REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


# def upload_files_to_yadisk(files):
#     start_time = time.time()

#     urls = []  # Список для сбора готовых ссылок.
#     if files is not None:  # Если были переданы изображения...
#         for file in files:  # ...для каждого изображения...

#             # 1. Ссылка на загрузку
#             response = requests.get(
#                 headers=AUTH_HEADERS,
#                 params={
#                     'path': f'app:/{file.filename}',
#                     'overwrite': True,
#                 },
#                 url=REQUEST_UPLOAD_URL,
#             )

#             # Загрузка
#             UPLOAD_URL = response.json()['href']
#             data = file.read()
#             response = requests.put(UPLOAD_URL, data)

#             # В location находится ссылка на расположение файла,
#             # может содержать закодированные символы.
#             location = urllib.parse.unquote(
#                 response.headers['Location']
#             ).replace('/disk', '')

#             # Запрос ссылки для скачивания.
#             response = requests.get(
#                 headers=AUTH_HEADERS,
#                 params={
#                     'path': location,
#                     # 'fields': 'href', 'templated'
#                 },
#                 url=DOWNLOAD_LINK_URL,
#             )

#             data = response.json()
#             url = data['href']
#             urls.append(url)

#     print('Итоговое время загрузки:', time.time() - start_time)
#     return urls


async def upload_file_and_get_url(session, file):
    # 1. Ссылка на загрузку
    async with session.get(
        headers=AUTH_HEADERS,
        params={
            'path': f'app:/{file.filename}',
            'overwrite': 'true',
        },
        url=REQUEST_UPLOAD_URL,
    ) as response:
        data = await response.json()

    # 2. Загрузка
    UPLOAD_URL = data['href']
    file_data = file.read()

    async with session.put(
        UPLOAD_URL,
        data=file_data,
    ) as response:

        location = urllib.parse.unquote(  # декодирование
            response.headers['Location']  # чтение заголовка Location
        ).replace(  # удаление /disk
            '/disk', ''
        )

    # 3. Запрос ссылки для скачивания.
    async with session.get(
        headers=AUTH_HEADERS,
        params={
            'path': location,
            # 'fields': 'href', 'templated'
        },
        url=DOWNLOAD_LINK_URL,
    ) as response:
        data = await response.json()

    url = data['href']
    return url, file.filename


# Асинхронная функция, создаёт задачи и запускает их.
async def async_upload_files_to_yadisk(files):
    # start_time = time.time()

    if files is not None:
        # Создать пустой список для асинхронных задач.
        tasks = []
        # Инициализировать единую сессию для работы с aiohttp.
        async with aiohttp.ClientSession() as session:
            for file in files:
                # Для каждого изображения создать асинхронную задачу.
                tasks.append(
                    asyncio.ensure_future(
                        # Передать в асинхронную функцию
                        # сессию и файл.
                        upload_file_and_get_url(
                            session, file
                        )  # [(url, filename), ...]
                    )
                )
            # После того как все задачи созданы, запустить их на выполнение.
            result = await asyncio.gather(*tasks)

        # print('Итоговое время загрузки:', time.time() - start_time)
        return result
