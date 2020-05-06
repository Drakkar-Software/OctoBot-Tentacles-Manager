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
from os.path import isfile
from shutil import rmtree

import aiohttp
import pytest
from os import path

from octobot_tentacles_manager.api.installer import install_all_tentacles
from octobot_tentacles_manager.configuration.tentacle_configuration import get_config, update_config, \
    factory_reset_config, get_config_schema_path
from octobot_tentacles_manager.constants import USER_TENTACLE_CONFIG_PATH, TENTACLES_PATH
from octobot_tentacles_manager.loaders.tentacle_loading import reload_tentacle_by_tentacle_class

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_get_config():
    _cleanup()
    async with aiohttp.ClientSession() as session:
        await install_all_tentacles(_tentacles_local_path(), aiohttp_session=session)
    from tentacles.Evaluator.RealTime import InstantFluctuationsEvaluator
    assert get_config(InstantFluctuationsEvaluator) == {
        "price_difference_threshold_percent": 1,
        "volume_difference_threshold_percent": 400
    }
    from tentacles.Services import RedditService
    assert get_config(RedditService) == {}
    _cleanup()


async def test_update_config():
    async with aiohttp.ClientSession() as session:
        await install_all_tentacles(_tentacles_local_path(), aiohttp_session=session)
    from tentacles.Evaluator.RealTime import InstantFluctuationsEvaluator
    config_update = {
        "price_difference_threshold_percent": 2,
        "plop": 42
    }
    update_config(InstantFluctuationsEvaluator, config_update)
    assert get_config(InstantFluctuationsEvaluator) == {
        "price_difference_threshold_percent": 2,
        "volume_difference_threshold_percent": 400,
        "plop": 42
    }
    _cleanup()


async def test_factory_reset_config():
    async with aiohttp.ClientSession() as session:
        await install_all_tentacles(_tentacles_local_path(), aiohttp_session=session)
    from tentacles.Evaluator.RealTime import InstantFluctuationsEvaluator
    config_update = {
        "price_difference_threshold_percent": 2,
        "plop": 42
    }
    update_config(InstantFluctuationsEvaluator, config_update)
    reload_tentacle_by_tentacle_class()
    factory_reset_config(InstantFluctuationsEvaluator)
    assert get_config(InstantFluctuationsEvaluator) == {
        "price_difference_threshold_percent": 1,
        "volume_difference_threshold_percent": 400
    }
    _cleanup()


async def test_get_config_schema_path():
    async with aiohttp.ClientSession() as session:
        await install_all_tentacles(_tentacles_local_path(), aiohttp_session=session)
    from tentacles.Evaluator.RealTime import InstantFluctuationsEvaluator
    assert isfile(get_config_schema_path(InstantFluctuationsEvaluator))
    _cleanup()


def _tentacles_local_path():
    return path.join("tests", "static", "tentacles.zip")


def _cleanup():
    if path.exists(TENTACLES_PATH):
        rmtree(TENTACLES_PATH)
    if path.exists(USER_TENTACLE_CONFIG_PATH):
        rmtree(USER_TENTACLE_CONFIG_PATH)
