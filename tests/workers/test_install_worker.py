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
import aiohttp
import pytest
from logging import INFO
from shutil import rmtree
from os import walk, path

from octobot_commons.logging.logging_util import set_logging_level
from octobot_tentacles_manager.constants import USER_TENTACLE_CONFIG_PATH, USER_TENTACLE_SPECIFIC_CONFIG_PATH, \
    TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR, USER_TENTACLE_CONFIG_FILE_PATH, TENTACLES_PATH
from octobot_tentacles_manager.installers.install_worker import InstallWorker

# All test coroutines will be treated as marked.
from octobot_tentacles_manager.tentacle_data.tentacle_data import TentacleData
from octobot_tentacles_manager.util.tentacle_fetching import fetch_and_extract_tentacles

pytestmark = pytest.mark.asyncio

temp_dir = "temp_tests"


async def test_create_missing_tentacles_arch():
    _cleanup()
    worker = InstallWorker("", TENTACLES_PATH, False, None)
    await worker.create_missing_tentacles_arch()
    trading_mode_files_count = sum(1 for _ in walk(TENTACLES_PATH))
    assert trading_mode_files_count == 25
    assert path.exists(USER_TENTACLE_CONFIG_PATH)
    _cleanup()


async def test_install_two_tentacles():
    _cleanup()
    _enable_loggers()
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
    worker = InstallWorker(temp_dir, TENTACLES_PATH, False, None)
    worker.default_tentacle_config = path.join("tests", "static", "default_tentacle_config.json")
    assert await worker.install_tentacles(["instant_fluctuations_evaluator", "generic_exchange_importer"]) == 0

    # test installed files
    trading_mode_files_count = sum(1 for _ in walk(path.join(TENTACLES_PATH, "Trading", "Mode")))
    assert trading_mode_files_count == 1
    backtesting_mode_files_count = sum(1 for _ in walk(path.join(TENTACLES_PATH, "Backtesting", "importers")))
    assert backtesting_mode_files_count == 7
    config_files = [f for f in walk(USER_TENTACLE_SPECIFIC_CONFIG_PATH)]
    config_files_count = len(config_files)
    assert config_files_count == 1
    assert "InstantFluctuationsEvaluator.json" in config_files[0][2]
    assert "DailyTradingMode.json" not in config_files[0][2]
    assert len(config_files[0][2]) == 1

    # test tentacles config
    with open(USER_TENTACLE_CONFIG_FILE_PATH, "r") as config_f:
        assert json.load(config_f) == {
            'tentacle_activation': {
                'InstantFluctuationsEvaluator': True
            }
        }
    _cleanup()


async def test_install_one_tentacle_with_requirement():
    async with aiohttp.ClientSession() as session:
        _cleanup()
        _enable_loggers()
        await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
        worker = InstallWorker(temp_dir, TENTACLES_PATH, False, session)
        worker.default_tentacle_config = path.join("tests", "static", "default_tentacle_config.json")
        assert await worker.install_tentacles(["reddit_service_feed"]) == 0

    # test installed files
    trading_mode_files_count = sum(1 for _ in walk(path.join(TENTACLES_PATH, "Trading", "Mode")))
    assert trading_mode_files_count == 1
    config_files = [f for f in walk(USER_TENTACLE_SPECIFIC_CONFIG_PATH)]
    assert len(config_files) == 1
    assert len(config_files[0][2]) == 0

    # test tentacles config
    with open(USER_TENTACLE_CONFIG_FILE_PATH, "r") as config_f:
        assert json.load(config_f) == {
            'tentacle_activation': {}
        }
    assert path.exists(path.join("tentacles", "Services", "reddit_service", "reddit_service.py"))
    _cleanup()


async def test_install_all_tentacles():
    _cleanup()
    _enable_loggers()
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
    worker = InstallWorker(temp_dir, TENTACLES_PATH, False, None)
    worker.default_tentacle_config = path.join("tests", "static", "default_tentacle_config.json")
    assert await worker.install_tentacles() == 0

    # test installed files
    trading_mode_files_count = sum(1 for _ in walk(path.join(TENTACLES_PATH, "Trading", "Mode")))
    assert trading_mode_files_count == 5
    config_files = [f for f in walk(USER_TENTACLE_SPECIFIC_CONFIG_PATH)]
    config_files_count = len(config_files)
    assert config_files_count == 1
    assert "DailyTradingMode.json" in config_files[0][2]
    assert len(config_files[0][2]) == 4

    # test tentacles config
    with open(USER_TENTACLE_CONFIG_FILE_PATH, "r") as config_f:
        assert json.load(config_f) == {
            'tentacle_activation': {
                'InstantFluctuationsEvaluator': True,
                'RedditForumEvaluator': False,
                'SimpleMixedStrategyEvaluator': True,
                'DailyTradingMode': True
            }
        }
    _cleanup()


async def test_install_all_tentacles_twice():
    _cleanup()
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
    worker = InstallWorker(temp_dir, TENTACLES_PATH, False, None)
    worker.default_tentacle_config = path.join("tests", "static", "default_tentacle_config.json")
    assert await worker.install_tentacles() == 0
    assert await worker.install_tentacles() == 0
    trading_mode_files_count = sum(1 for _ in walk(path.join(TENTACLES_PATH, "Trading", "Mode")))
    assert trading_mode_files_count == 5
    _cleanup()


async def test_install_all_tentacles_fetching_requirements():
    async with aiohttp.ClientSession() as session:
        _cleanup()
        _enable_loggers()
        await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "requirements_tentacles.zip"), None)
        worker = InstallWorker(temp_dir, TENTACLES_PATH, False, session)
        worker.default_tentacle_config = path.join("tests", "static", "default_tentacle_config.json")
        assert await worker.install_tentacles() == 0

    trading_mode_files_count = sum(1 for _ in walk(path.join(TENTACLES_PATH, "Trading", "Mode")))
    assert trading_mode_files_count == 5
    config_files = [f for f in walk(USER_TENTACLE_SPECIFIC_CONFIG_PATH)]
    config_files_count = len(config_files)
    assert config_files_count == 1
    # ensure fetched InstantFluctuationsEvaluator requirement
    assert "InstantFluctuationsEvaluator.json" in config_files[0][2]
    assert path.exists(path.join("tentacles", "Evaluator", "RealTime",
                                 "instant_fluctuations_evaluator", "instant_fluctuations_evaluator.py"))
    assert len(config_files[0][2]) == 4
    _cleanup()


def _enable_loggers():
    for clazz in [InstallWorker, TentacleData]:
        set_logging_level(clazz.__name__, INFO)


def _cleanup():
    if path.exists(temp_dir):
        rmtree(temp_dir)
    if path.exists(TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR):
        rmtree(TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR)
    if path.exists(TENTACLES_PATH):
        rmtree(TENTACLES_PATH)
    if path.exists(USER_TENTACLE_CONFIG_PATH):
        rmtree(USER_TENTACLE_CONFIG_PATH)
