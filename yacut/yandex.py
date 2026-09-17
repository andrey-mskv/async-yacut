from . import app
import requests

# import asyncio
# import aiohttp
import time

# import json

# from pprint import pprint
import urllib

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'

AUTH_HEADERS = {'Authorization': f"OAuth {app.config['DISK_TOKEN']}"}

REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


# # Запрос информации о диске
# DISK_INFO_URL = f'{API_HOST}{API_VERSION}/disk/'
# response = requests.get(url=DISK_INFO_URL, headers=AUTH_HEADERS)
# pprint(response.json())

# Запрос ссылки для загрузки
# payload = {'path': 'app:/test.txt', 'overwrite': True, 'fields': 'href'}
# link_response = requests.get(
#     headers=AUTH_HEADERS, params=payload, url=REQUEST_UPLOAD_URL
# )

# print(link_response.json())

# Загрузка файла
# UPLOAD_URL = link_response.json()['href']

# with open('test.txt', 'rb') as file:
#     upload_response = requests.put(UPLOAD_URL, data=file)

# Расположение файла находится в заголовке Location.
# location = upload_response.headers['Location']
# Декодировать строку при помощи модуля urllib.
# location = urllib.parse.unquote(location)
# Убрать первую часть расположения файла /disk,
# она не понадобится.
# location = location.replace('/disk', '')
# print(location)

# Запрос ссылки для скачивания
# download_response = requests.get(
#     headers=AUTH_HEADERS, params={'path': location}, url=DOWNLOAD_LINK_URL
# )

# print(download_response.json()['href'])


def upload_files_to_yadisk(files):
    start_time = time.time()

    urls = []  # Список для сбора готовых ссылок.
    if files is not None:  # Если были переданы изображения...
        for file in files:  # ...для каждого изображения...

            # 1. Ссылка на загрузку
            response = requests.get(
                headers=AUTH_HEADERS,
                params={
                    'path': f'app:/{file.filename}',
                    'overwrite': True,
                },
                url=REQUEST_UPLOAD_URL,
            )

            # Загрузка
            UPLOAD_URL = response.json()['href']
            data = file.read()
            response = requests.put(UPLOAD_URL, data)

            # В location находится ссылка на расположение файла,
            # может содержать закодированные символы.
            location = urllib.parse.unquote(
                response.headers['Location']
            ).replace('/disk', '')

            # Запрос ссылки для скачивания.
            response = requests.get(
                headers=AUTH_HEADERS,
                params={
                    'path': location,
                    # 'fields': 'href', 'templated'
                },
                url=DOWNLOAD_LINK_URL,
            )

            data = response.json()
            url = data['href']
            urls.append(url)

    print('Итоговое время загрузки:', time.time() - start_time)
    return urls


# # Асинхронная функция, которая создаёт задачи и запускает их.
# async def async_upload_files_to_yandex(images):
#     start_time = time.time()

#     if images is not None:
#         # Создать пустой список для асинхронных задач.
#         tasks = []
#         # Инициализировать единую сессию для работы с aiohttp.
#         async with aiohttp.ClientSession() as session:
#             for image in images:
#                 # Для каждого изображения создать асинхронную задачу.
#                 tasks.append(
#                     asyncio.ensure_future(
#                         # Передать в асинхронную
#                         # функцию сессию и изображение.
#                         upload_file_and_get_url(session, image)
#                     )
#                 )
#             # После того как все задачи созданы, запустить их на выполнение.
#             urls = await asyncio.gather(*tasks)

#         print('Итоговое время загрузки:', time.time() - start_time)
#         return urls
