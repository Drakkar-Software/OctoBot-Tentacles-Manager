#  Drakkar-Software OctoBot-Tentacles-Manager
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import os
import aiohttp

import octobot_tentacles_manager.uploaders.uploader as uploader


class NexusUploader(uploader.Uploader):
    ENV_NEXUS_USERNAME = "NEXUS_USERNAME"
    ENV_NEXUS_PASSWORD = "NEXUS_PASSWORD"
    ENV_NEXUS_URL = "NEXUS_URL"
    NEXUS_EXPECTED_RESPONSE_STATUS = [200, 201]

    def __init__(self):
        super().__init__()
        self.nexus_username: str = os.getenv(NexusUploader.ENV_NEXUS_USERNAME)
        self.nexus_password: str = os.getenv(NexusUploader.ENV_NEXUS_PASSWORD)
        self.nexus_url: str = os.getenv(NexusUploader.ENV_NEXUS_URL)

    async def upload_file(self, upload_path: str, file_path: str, destination_file_name: str = None) -> int:
        """
        Upload file on nexus wrapper
        :param upload_path: the upload path, the internal path after self.nexus_url
        :param file_path: the file local path
        :param destination_file_name: the file name on nexus (optional : default file_path basename)
        :return: the result of _upload
        """
        dest_file_name: str = destination_file_name if destination_file_name is not None else os.path.basename(
            file_path)
        upload_file_url: str = f"{self.nexus_url}/{upload_path}/{dest_file_name}"
        self.logger.info(f"Uploading {file_path} to nexus at {upload_file_url}...")
        return await self._upload(file_url_on_nexus=upload_file_url, local_file_path=file_path)

    async def upload_folder(self, upload_path: str, folder_path: str, destination_folder_name: str = None) -> int:
        """
        Upload folder content on nexus wrapper
        :param upload_path: the upload path, the internal path after self.nexus_url
        :param folder_path: the folder local path
        :param destination_folder_name: the folder name on nexus (optional : default folder_path basename)
        :return: the sum of all of _upload returns
        """
        error_count: int = 0
        dest_folder_name: str = destination_folder_name \
            if destination_folder_name is not None else os.path.basename(folder_path)
        upload_folder_url: str = f"{self.nexus_url}/{upload_path}/{dest_folder_name}"
        for file_path in os.listdir(folder_path):
            upload_file_url = f"{upload_folder_url}/{file_path}"
            self.logger.debug(f"Uploading {file_path} to nexus at {upload_file_url}...")
            error_count += await self._upload(file_url_on_nexus=upload_file_url,
                                              local_file_path=os.path.join(folder_path, file_path))
        return error_count

    async def _upload(self, file_url_on_nexus: str, local_file_path: str):
        """
        Upload a file on nexus
        :param file_url_on_nexus: the complete upload url
        :param local_file_path: the local file path
        :return: 0 if upload succeed else 1
        """
        async with aiohttp.ClientSession() as aiohttp_session:
            with aiohttp.MultipartWriter('mixed') as multipart_writer:
                multipart_writer.append(open(local_file_path, 'rb'))
                async with aiohttp_session.put(file_url_on_nexus,
                                               data=multipart_writer,
                                               auth=aiohttp.BasicAuth(self.nexus_username,
                                                                      self.nexus_password)) as response:
                    if response.status in NexusUploader.NEXUS_EXPECTED_RESPONSE_STATUS:
                        return 0
                    self.logger.error(f"Failed to upload file on nexus "
                                      f"(status code {response.status}) : {await response.text()}")
                    return 1
