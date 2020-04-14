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
from os.path import exists
from shutil import rmtree
import aiohttp
import pytest
from os import path, remove, mkdir

from octobot_tentacles_manager.api.creator import create_tentacles_package
from octobot_tentacles_manager.api.installer import install_all_tentacles
from octobot_tentacles_manager.constants import TENTACLES_PATH, PYTHON_INIT_FILE, TENTACLES_EVALUATOR_PATH, \
    TENTACLES_EVALUATOR_REALTIME_PATH, TENTACLE_METADATA, METADATA_VERSION, METADATA_ORIGIN_PACKAGE, \
    METADATA_TENTACLES, METADATA_TENTACLES_REQUIREMENTS, METADATA_DEV_MODE, TENTACLES_TRADING_PATH, \
    TENTACLES_TRADING_MODE_PATH, TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER
from octobot_tentacles_manager.managers.tentacles_setup_manager import TentaclesSetupManager

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio
TENTACLE_PACKAGE = "tentacle_package"


async def test_create_folder_tentacles_package():
    _cleanup()
    async with aiohttp.ClientSession() as session:
        assert await install_all_tentacles(_tentacles_local_path(), aiohttp_session=session) == 0

    # set instant_fluctuations_evaluator in dev mode
    tentacle_path = path.join(TENTACLES_PATH, TENTACLES_EVALUATOR_PATH, TENTACLES_EVALUATOR_REALTIME_PATH)
    with open(path.join(tentacle_path, "instant_fluctuations_evaluator", TENTACLE_METADATA), "w+") as metadata:
        new_metadata = {
          METADATA_VERSION: "1.2.0",
          METADATA_ORIGIN_PACKAGE: "OctoBot-Default-Tentacles",
          METADATA_TENTACLES: ["InstantFluctuationsEvaluator"],
          METADATA_TENTACLES_REQUIREMENTS: [],
          METADATA_DEV_MODE: True
        }
        json.dump(new_metadata, metadata)

    # add generated python file
    random_content = "123"
    generated_file_path = path.join(TENTACLES_PATH, "file.pyc")
    with open(generated_file_path, "w+") as generated_file:
        generated_file.write(random_content)
    # add generated python folder
    generated_folder_path = path.join(TENTACLES_PATH, TENTACLES_TRADING_PATH, "__pycache__")
    mkdir(generated_folder_path)

    # create folder to force folder merge
    mkdir(TENTACLE_PACKAGE)
    mkdir(path.join(TENTACLE_PACKAGE, TENTACLES_TRADING_PATH))
    with open(path.join(TENTACLE_PACKAGE, "rnd"), "w+") as rand_file:
        rand_file.write(random_content)

    assert await create_tentacles_package(TENTACLE_PACKAGE, in_zip=False) == 0
    assert path.exists(TENTACLE_PACKAGE)

    # random init file still here
    with open(path.join(TENTACLE_PACKAGE, "rnd")) as rand_file:
        assert random_content == rand_file.read()

    # generated file not copied
    assert not path.exists(path.join(TENTACLE_PACKAGE, "file.pyc"))

    # generated folder not copied
    assert not path.exists(path.join(TENTACLE_PACKAGE, TENTACLES_TRADING_PATH, "__pycache__"))

    # did not add instant_fluctuations_evaluator (in dev-mode)
    package_tentacle_path = path.join(TENTACLE_PACKAGE, TENTACLES_EVALUATOR_PATH, TENTACLES_EVALUATOR_REALTIME_PATH)
    assert not path.exists(path.join(package_tentacle_path, "instant_fluctuations_evaluator"))

    # added other_instant_fluctuations_evaluator
    assert path.exists(path.join(package_tentacle_path, "other_instant_fluctuations_evaluator"))

    # added daily_trading_mode
    trading_mode_tentacle_path = path.join(TENTACLE_PACKAGE, TENTACLES_TRADING_PATH, TENTACLES_TRADING_MODE_PATH)
    assert path.exists(path.join(trading_mode_tentacle_path, "daily_trading_mode"))
    assert path.exists(path.join(trading_mode_tentacle_path, "daily_trading_mode", "daily_trading_mode.py"))

    # removed python init files
    assert not path.exists(path.join(TENTACLE_PACKAGE, PYTHON_INIT_FILE))
    evaluator_path = path.join(TENTACLE_PACKAGE, TENTACLES_EVALUATOR_PATH)
    assert not path.exists(path.join(evaluator_path, PYTHON_INIT_FILE))
    assert not path.exists(path.join(evaluator_path, TENTACLES_EVALUATOR_REALTIME_PATH, PYTHON_INIT_FILE))

    _cleanup()


async def test_create_zipped_tentacles_package():
    _cleanup()
    tentacle_package = "tentacle_package.zip"
    async with aiohttp.ClientSession() as session:
        assert await install_all_tentacles(_tentacles_local_path(), aiohttp_session=session) == 0
    assert await create_tentacles_package(tentacle_package) == 0
    assert path.exists(tentacle_package)
    assert not path.exists(TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)
    remove(tentacle_package)
    _cleanup()


def _tentacles_local_path():
    return path.join("tests", "static", "tentacles.zip")


def _cleanup():
    if exists(TENTACLES_PATH):
        TentaclesSetupManager.delete_tentacles_arch(force=True)
    if exists(TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER):
        rmtree(TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)
    if exists(TENTACLE_PACKAGE):
        rmtree(TENTACLE_PACKAGE)