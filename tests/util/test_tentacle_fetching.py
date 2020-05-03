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
import aiohttp
import pytest
from os import path, walk

from octobot_tentacles_manager.constants import TENTACLE_TYPES, TENTACLES_ARCHIVE_ROOT, DEFAULT_TENTACLES_URL
from octobot_tentacles_manager.util.tentacle_fetching import fetch_and_extract_tentacles, cleanup_temp_dirs

# All test coroutines will be treated as marked.

pytestmark = pytest.mark.asyncio

temp_dir = "tests_temp"


async def test_fetch_and_extract_tentacles_using_download():
    _cleanup()
    # ensure cleanup is working
    assert not path.isdir(temp_dir)
    session = aiohttp.ClientSession()
    await fetch_and_extract_tentacles(temp_dir, DEFAULT_TENTACLES_URL, session)
    _test_temp_tentacles()
    _cleanup()


async def test_fetch_and_extract_tentacles_using_download_with_wrong_url():
    _cleanup()
    # ensure cleanup is working
    assert not path.isdir(temp_dir)
    session = aiohttp.ClientSession()
    with pytest.raises(RuntimeError):
        await fetch_and_extract_tentacles(temp_dir, DEFAULT_TENTACLES_URL+"1213113a", session)
    _cleanup()


async def test_fetch_and_extract_tentacles_using_download_without_session():
    _cleanup()
    with pytest.raises(RuntimeError):
        await fetch_and_extract_tentacles(temp_dir, DEFAULT_TENTACLES_URL, None)
    assert not path.isdir(temp_dir)


async def test_fetch_and_extract_tentacles_using_local_file():
    _cleanup()
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
    _test_temp_tentacles()
    _cleanup()


def _test_temp_tentacles():
    assert all(path.isdir(_tentacle_path(tentacle_type)) for tentacle_type in TENTACLE_TYPES)
    # assert sub directories also got extracted
    total_files_count = sum(1 for _ in walk(temp_dir))
    assert total_files_count > len(TENTACLE_TYPES)


def _tentacle_path(tentacle_type):
    return path.join(temp_dir, TENTACLES_ARCHIVE_ROOT, tentacle_type)


def _cleanup():
    cleanup_temp_dirs(temp_dir)
