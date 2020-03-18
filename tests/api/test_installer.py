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
from os.path import exists

import aiohttp
import pytest
from os import path

from octobot_commons.constants import TENTACLES_PATH
from octobot_tentacles_manager.api.installer import install_all_tentacles, install_tentacles
from octobot_tentacles_manager.managers.tentacles_setup_manager import TentaclesSetupManager

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_install_all_tentacles():
    _cleanup(False)
    async with aiohttp.ClientSession() as session:
        assert await install_all_tentacles(_tentacles_local_path(), aiohttp_session=session) == 0
    _cleanup()


async def test_install_one_tentacle_with_requirement():
    async with aiohttp.ClientSession() as session:
        assert await install_tentacles(["reddit_service_feed"], _tentacles_local_path(), aiohttp_session=session) == 0
        assert path.exists(path.join("tentacles", "Services", "reddit_service", "reddit_service.py"))
    _cleanup()


def _tentacles_local_path():
    return path.join("tests", "static", "tentacles.zip")


def _cleanup(raises=True):
    if exists(TENTACLES_PATH):
        TentaclesSetupManager.delete_tentacles_arch(force=True, raises=raises)
