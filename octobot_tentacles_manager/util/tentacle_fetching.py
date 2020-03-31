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
import aiofiles
from zipfile import ZipFile
from os import remove, path
from shutil import rmtree

from octobot_tentacles_manager.constants import TENTACLE_TYPES, TENTACLES_ARCHIVE_ROOT

DOWNLOADED_DATA_CHUNK_SIZE = 60000


async def fetch_and_extract_tentacles(tentacles_temp_dir, tentacles_path_or_url, aiohttp_session, merge_dirs=False):
    compressed_file = tentacles_path_or_url
    should_download = _is_url(tentacles_path_or_url)
    if should_download:
        if aiohttp_session is None:
            raise RuntimeError("Missing aiohttp_session argument")
        compressed_file = f"downloaded_{tentacles_temp_dir}"
        await _download_tentacles(compressed_file, tentacles_path_or_url, aiohttp_session)
    await _extract_tentacles(compressed_file, tentacles_temp_dir, should_download, merge_dirs)


def cleanup_temp_dirs(target_path):
    if path.exists(target_path):
        rmtree(target_path)


async def _download_tentacles(target_file, download_URL, aiohttp_session):
    async with aiohttp_session.get(download_URL) as resp:
        async with aiofiles.open(target_file, 'wb+') as downloaded_file:
            while True:
                chunk = await resp.content.read(DOWNLOADED_DATA_CHUNK_SIZE)
                if not chunk:
                    # resp.content.read returns an empty chunk when completed
                    break
                await downloaded_file.write(chunk)


async def _extract_tentacles(source_path, target_path, remove_source_file, merge_dirs):
    if path.exists(target_path) and path.isdir(target_path) and not merge_dirs:
        rmtree(target_path)
    with ZipFile(source_path) as zipped_tentacles:
        for archive_member in zipped_tentacles.namelist():
            if _is_tentacle_valid_tentacle_file(archive_member):
                zipped_tentacles.extract(archive_member, target_path)
    if remove_source_file:
        remove(source_path)


def _is_tentacle_valid_tentacle_file(archive_member):
    member_path = archive_member.split("/")
    return len(member_path) >= 2 \
        and member_path[0] == TENTACLES_ARCHIVE_ROOT \
        and member_path[1] in TENTACLE_TYPES


def _is_url(string):
    return string.startswith("https://") \
           or string.startswith("http://") \
           or string.startswith("ftp://") \
           or string.startswith("sftp://")
