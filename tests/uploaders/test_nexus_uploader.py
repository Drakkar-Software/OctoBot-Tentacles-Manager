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
import json
import os
import shutil

import aiofiles
import aiohttp
import time

import pytest

import octobot_tentacles_manager.api.uploader as uploader_api
import octobot_tentacles_manager.uploaders as uploaders

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

TEST_NEXUS_DIRECTORY = "nexus-tests"
TEST_NEXUS_PATH = "officials/base/dev/tests/tentacle-manager/"
TEST_NEXUS_FILE_NAME = "test"


@pytest.yield_fixture()
async def nexus_tests():
    if os.path.exists(TEST_NEXUS_DIRECTORY):
        shutil.rmtree(TEST_NEXUS_DIRECTORY)
    os.mkdir(TEST_NEXUS_DIRECTORY)
    yield
    if os.path.exists(TEST_NEXUS_DIRECTORY):
        shutil.rmtree(TEST_NEXUS_DIRECTORY)


async def test_upload_file(nexus_tests):
    nexus_test_file_name: str = f"{time.time_ns()}.json"
    local_file_name: str = os.path.join(TEST_NEXUS_DIRECTORY, f"{TEST_NEXUS_FILE_NAME}.json")

    # test upload file
    with open(local_file_name, "w") as test_file:
        test_file.write(json.dumps("{'test-key': 1}"))
    assert await uploader_api.upload_file_or_folder_to_nexus(nexus_path=TEST_NEXUS_PATH,
                                                             artifact_path=local_file_name,
                                                             artifact_alias=nexus_test_file_name) == 0
    # test download file
    downloaded_file_path: str = await download_file_from_nexus(f"{TEST_NEXUS_PATH}/{nexus_test_file_name}",
                                                               "downloaded_file")

    with open(downloaded_file_path, "r") as downloaded_file:
        assert json.loads(downloaded_file.read()) == {
            'test-key': 1
        }


async def test_upload_folder():
    pass


async def download_file_from_nexus(file_url: str, local_file_name: str) -> str:
    downloaded_file_path: str = os.path.join(TEST_NEXUS_DIRECTORY, local_file_name)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{os.getenv(uploaders.NexusUploader.ENV_NEXUS_URL)}/{file_url}") as resp:
            assert resp.status == 200
            async with aiofiles.open(downloaded_file_path, mode='wb') as downloaded_file:
                downloaded_file.write(await resp.read())
    return downloaded_file_path
