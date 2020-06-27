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
    TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR, USER_TENTACLE_CONFIG_FILE_PATH, TENTACLES_PATH, DEFAULT_BOT_PATH, \
    UNKNOWN_TENTACLES_PACKAGE_LOCATION
from octobot_tentacles_manager.workers.install_worker import InstallWorker

# All test coroutines will be treated as marked.
from octobot_tentacles_manager.models.tentacle import Tentacle
from octobot_tentacles_manager.util.tentacle_fetching import fetch_and_extract_tentacles

pytestmark = pytest.mark.asyncio

temp_dir = "temp_tests"


async def test_install_two_tentacles():
    _cleanup()
    _enable_loggers()
    tentacles_path = path.join("tests", "static", "tentacles.zip")
    await fetch_and_extract_tentacles(temp_dir, tentacles_path, None)
    worker = InstallWorker(temp_dir, TENTACLES_PATH, DEFAULT_BOT_PATH, False, None)
    worker.tentacles_path_or_url = tentacles_path
    worker.tentacles_setup_manager.default_tentacle_config = \
        path.join("tests", "static", "default_tentacle_config.json")
    assert await worker.process(["instant_fluctuations_evaluator", "generic_exchange_importer"]) == 0

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
            'registered_tentacles': {
                'OctoBot-Default-Tentacles': tentacles_path
            },
            'tentacle_activation': {
                'Backtesting': {
                    'GenericExchangeDataImporter': True
                },
                'Evaluator': {
                    'InstantFluctuationsEvaluator': True
                }
            }
        }
    _cleanup()


async def test_install_one_tentacle_with_requirement():
    async with aiohttp.ClientSession() as session:
        _cleanup()
        _enable_loggers()
        await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
        worker = InstallWorker(temp_dir, TENTACLES_PATH, DEFAULT_BOT_PATH, False, session)
        worker.tentacles_setup_manager.default_tentacle_config = \
            path.join("tests", "static", "default_tentacle_config.json")
        assert await worker.process(["reddit_service_feed"]) == 0

    # test removed temporary requirements files
    assert not path.exists(TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR)

    # test installed files
    trading_mode_files_count = sum(1 for _ in walk(path.join(TENTACLES_PATH, "Trading", "Mode")))
    assert trading_mode_files_count == 1
    config_files = [f for f in walk(USER_TENTACLE_SPECIFIC_CONFIG_PATH)]
    assert len(config_files) == 1
    assert len(config_files[0][2]) == 0

    # test tentacles config
    with open(USER_TENTACLE_CONFIG_FILE_PATH, "r") as config_f:
        assert json.load(config_f) == {
            'registered_tentacles': {
                'OctoBot-Default-Tentacles': UNKNOWN_TENTACLES_PACKAGE_LOCATION
            },
            'tentacle_activation': {
                'Services': {
                    'RedditService': True,
                    'RedditServiceFeed': True
                }
            }
        }
    assert path.exists(path.join("tentacles", "Services", "Services_bases", "reddit_service", "reddit_service.py"))
    _cleanup()


async def test_install_all_tentacles():
    _cleanup()
    _enable_loggers()
    tentacles_path = path.join("tests", "static", "tentacles.zip")
    await fetch_and_extract_tentacles(temp_dir, tentacles_path, None)
    worker = InstallWorker(temp_dir, TENTACLES_PATH, DEFAULT_BOT_PATH, False, None)
    worker.tentacles_path_or_url = tentacles_path
    worker.tentacles_setup_manager.default_tentacle_config = \
        path.join("tests", "static", "default_tentacle_config.json")
    assert await worker.process() == 0

    # test installed files
    trading_mode_files_count = sum(1 for _ in walk(path.join(TENTACLES_PATH, "Trading", "Mode")))
    assert trading_mode_files_count == 5
    config_files = [f for f in walk(USER_TENTACLE_SPECIFIC_CONFIG_PATH)]
    config_files_count = len(config_files)
    assert config_files_count == 1
    assert "DailyTradingMode.json" in config_files[0][2]
    assert len(config_files[0][2]) == 5

    # test tentacles config
    with open(USER_TENTACLE_CONFIG_FILE_PATH, "r") as config_f:
        assert json.load(config_f) == {
            'registered_tentacles': {
                'OctoBot-Default-Tentacles': tentacles_path
            },
            'tentacle_activation': {
                'Backtesting': {
                    'GenericExchangeDataImporter': True
                },
                'Evaluator': {
                    'InstantFluctuationsEvaluator': True,
                    'OtherInstantFluctuationsEvaluator': False,
                    'OverallStateAnalyser': True,
                    'RedditForumEvaluator': False,
                    'SecondOtherInstantFluctuationsEvaluator': False,
                    'SimpleMixedStrategyEvaluator': True,
                    'TextAnalysis': True
                },
                'Services': {
                    'RedditService': True,
                    'RedditServiceFeed': True
                },
                'Trading': {
                    'DailyTradingMode': True
                }
            }
        }
    _cleanup()


async def test_install_all_tentacles_twice():
    _cleanup()
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
    worker = InstallWorker(temp_dir, TENTACLES_PATH, DEFAULT_BOT_PATH, False, None)
    worker.tentacles_setup_manager.default_tentacle_config = \
        path.join("tests", "static", "default_tentacle_config.json")
    assert await worker.process() == 0
    assert await worker.process() == 0
    trading_mode_files_count = sum(1 for _ in walk(path.join(TENTACLES_PATH, "Trading", "Mode")))
    assert trading_mode_files_count == 5
    _cleanup()


async def test_install_all_tentacles_fetching_requirements():
    async with aiohttp.ClientSession() as session:
        _cleanup()
        _enable_loggers()
        await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "requirements_tentacles.zip"), None)
        worker = InstallWorker(temp_dir, TENTACLES_PATH, DEFAULT_BOT_PATH, False, session)
        worker.tentacles_setup_manager.default_tentacle_config = \
            path.join("tests", "static", "default_tentacle_config.json")
        assert await worker.process() == 0

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
    set_logging_level([clazz.__name__ for clazz in [InstallWorker, Tentacle]], INFO)


def _cleanup():
    if path.exists(temp_dir):
        rmtree(temp_dir)
    if path.exists(TENTACLES_PATH):
        rmtree(TENTACLES_PATH)
    if path.exists(USER_TENTACLE_CONFIG_PATH):
        rmtree(USER_TENTACLE_CONFIG_PATH)
