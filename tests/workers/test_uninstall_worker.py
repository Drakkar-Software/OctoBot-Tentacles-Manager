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
import pytest
from logging import INFO
from shutil import rmtree
from os import walk, path

from octobot_commons.logging.logging_util import set_logging_level
from octobot_tentacles_manager.constants import USER_TENTACLE_CONFIG_PATH, TENTACLES_PATH, \
    TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR, USER_TENTACLE_CONFIG_FILE_PATH
from octobot_tentacles_manager.installers.install_worker import InstallWorker

# All test coroutines will be treated as marked.
from octobot_tentacles_manager.tentacle_data.tentacle_data import TentacleData
from octobot_tentacles_manager.uninstallers.uninstall_worker import UninstallWorker
from octobot_tentacles_manager.util.tentacle_fetching import fetch_and_extract_tentacles

pytestmark = pytest.mark.asyncio

temp_dir = "temp_tests"


async def test_uninstall_two_tentacles():
    _cleanup()
    _enable_loggers()
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
    install_worker = InstallWorker(temp_dir, TENTACLES_PATH, False, None)
    install_worker.default_tentacle_config = path.join("tests", "static", "default_tentacle_config.json")
    assert await install_worker.install_tentacles() == 0
    tentacles_files_count = sum(1 for _ in walk(TENTACLES_PATH))
    assert tentacles_files_count > 60

    uninstall_worker = UninstallWorker(None, TENTACLES_PATH, False, None)
    uninstall_worker.default_tentacle_config = path.join("tests", "static", "default_tentacle_config.json")
    assert await uninstall_worker.uninstall_tentacles(["instant_fluctuations_evaluator", "generic_exchange_importer"]) == 0
    tentacles_files_count = sum(1 for _ in walk(TENTACLES_PATH))
    assert tentacles_files_count < 60
    with open(USER_TENTACLE_CONFIG_FILE_PATH, "r") as config_f:
        assert json.load(config_f) == {
            'tentacle_activation': {
                'DailyTradingMode': True,
                'RedditForumEvaluator': False,
                'SimpleMixedStrategyEvaluator': True
            }
        }
    _cleanup()


async def test_uninstall_all_tentacles():
    _cleanup()
    _enable_loggers()
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
    install_worker = InstallWorker(temp_dir, TENTACLES_PATH, False, None)
    install_worker.default_tentacle_config = path.join("tests", "static", "default_tentacle_config.json")
    assert await install_worker.install_tentacles() == 0
    tentacles_files_count = sum(1 for _ in walk(TENTACLES_PATH))
    assert tentacles_files_count > 60

    uninstall_worker = UninstallWorker(None, TENTACLES_PATH, False, None)
    uninstall_worker.default_tentacle_config = path.join("tests", "static", "default_tentacle_config.json")
    assert await uninstall_worker.uninstall_tentacles() == 0
    tentacles_files_count = sum(1 for _ in walk(TENTACLES_PATH))
    assert tentacles_files_count == 25
    with open(USER_TENTACLE_CONFIG_FILE_PATH, "r") as config_f:
        assert json.load(config_f) == {
            'tentacle_activation': {}
        }
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
