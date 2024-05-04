import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def upload_file_to_yandex_disk(file_path, token):
    base_url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {"Authorization": f"OAuth {token}"}
    today_date = datetime.now().strftime("%Y-%m-%d")
    folder_path = f"фотоотчеты/{today_date}"
    file_name = file_path.split('/')[-1]  # Получение имени файла из полного пути

    async with aiohttp.ClientSession() as session:
        # Создание папки, если она не существует
        async with session.put(f"{base_url}?path=disk:/{folder_path}", headers=headers) as response:
            if response.status not in (201, 409):  # 409 - уже существует
                logger.error(f"Failed to create folder: {await response.text()}")
                return None

        # Получение ссылки для загрузки
        upload_params = {"path": f"disk:/{folder_path}/{file_name}"}
        async with session.get(f"{base_url}/upload", headers=headers, params=upload_params) as response:
            # print(response)
            if response.status != 200:
                logger.error(f"Failed to get upload link: {await response.text()}")
                return None
            upload_url = (await response.json()).get('href')

            # Загрузка файла
            if upload_url:
                with open(file_path, 'rb') as f:
                    async with session.put(upload_url, data=f) as upload_response:
                        if upload_response.status == 201:
                            # Публикация файла
                            publish_url = f"{base_url}/publish?path=disk:/{folder_path}/{file_name}"
                            async with session.put(publish_url, headers=headers) as publish_response:
                                if publish_response.status == 200:
                                    # Получение публичной ссылки
                                    info_url = f"{base_url}?path=disk:/{folder_path}/{file_name}&fields=public_url"
                                    async with session.get(info_url, headers=headers) as info_response:
                                        if info_response.status == 200:
                                            info_data = await info_response.json()
                                            public_url = info_data.get('public_url')
                                            return public_url
                                logger.error(f"Failed to publish file: {await publish_response.text()}")
                        else:
                            logger.error(f"Failed to upload file: {await upload_response.text()}")
            return None
