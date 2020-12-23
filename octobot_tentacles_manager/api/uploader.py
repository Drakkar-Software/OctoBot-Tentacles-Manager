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

import octobot_tentacles_manager.uploaders.nexus_uploader as nexus_uploader


async def upload_file_to_nexus(nexus_path: str, file_path: str, alias_file_name: str = None) -> int:
    uploader = nexus_uploader.NexusUploader()
    return await uploader.upload_file(upload_path=nexus_path,
                                      file_path=file_path,
                                      destination_file_name=alias_file_name)


async def upload_folder_to_nexus(nexus_path: str, folder_path: str, alias_folder_name: str = None) -> int:
    uploader = nexus_uploader.NexusUploader()
    return await uploader.upload_folder(upload_path=nexus_path,
                                        folder_path=folder_path,
                                        destination_folder_name=alias_folder_name)
