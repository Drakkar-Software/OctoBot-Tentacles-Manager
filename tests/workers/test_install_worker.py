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
from shutil import rmtree
from os import walk, path
import pytest

from octobot_tentacles_manager.installers.install_worker import InstallWorker

# All test coroutines will be treated as marked.
from octobot_tentacles_manager.util.tentacle_fetching import fetch_and_extract_tentacles

pytestmark = pytest.mark.asyncio

test_tentacle_path = "temp_tests"
temp_dir = "tests_temp"


async def test_create_missing_tentacles_arch():
    _cleanup()
    worker = InstallWorker("", test_tentacle_path, False)
    await worker.create_missing_tentacles_arch()
    trading_mode_files_count = sum(1 for _ in walk(test_tentacle_path))
    assert trading_mode_files_count == 24
    _cleanup()


async def test_install_all_tentacles():
    _cleanup()
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
    worker = InstallWorker(temp_dir, test_tentacle_path, False)
    await worker.install_all_tentacles()
    trading_mode_files_count = sum(1 for _ in walk(path.join(test_tentacle_path, "Trading", "Mode")))
    assert trading_mode_files_count == 5
    _cleanup()


async def test_install_all_tentacles_twice():
    _cleanup()
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
    worker = InstallWorker(temp_dir, test_tentacle_path, False)
    await worker.install_all_tentacles()
    await worker.install_all_tentacles()
    trading_mode_files_count = sum(1 for _ in walk(path.join(test_tentacle_path, "Trading", "Mode")))
    assert trading_mode_files_count == 5
    _cleanup()


def _cleanup():
    if path.exists(test_tentacle_path):
        rmtree(test_tentacle_path)
