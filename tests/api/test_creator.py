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
from os.path import exists, join, getsize
from shutil import rmtree
import aiohttp
import pytest
from os import path, remove, mkdir, scandir, walk

from octobot_tentacles_manager.api.creator import create_tentacles_package, create_all_tentacles_bundle
from octobot_tentacles_manager.api.installer import install_all_tentacles
from octobot_tentacles_manager.constants import DEFAULT_EXPORT_DIR, TENTACLES_PATH, \
    PYTHON_INIT_FILE, TENTACLES_EVALUATOR_PATH, \
    TENTACLES_EVALUATOR_REALTIME_PATH, TENTACLE_METADATA, METADATA_VERSION, METADATA_ORIGIN_PACKAGE, \
    METADATA_TENTACLES, METADATA_TENTACLES_REQUIREMENTS, METADATA_DEV_MODE, TENTACLES_TRADING_PATH, \
    TENTACLES_TRADING_MODE_PATH, TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER, TENTACLES_SERVICES_PATH, \
    TENTACLES_BACKTESTING_IMPORTERS_PATH, TENTACLES_BACKTESTING_PATH, TENTACLES_BACKTESTING_THIRD_LEVEL_EXCHANGES_PATH
from octobot_tentacles_manager.managers.tentacles_setup_manager import TentaclesSetupManager

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio
TENTACLE_PACKAGE = "tentacle_package"
TEST_EXPORT_DIR = "test_export_dir"


@pytest.yield_fixture()
async def install_tentacles():
    _cleanup()
    async with aiohttp.ClientSession() as session:
        assert await install_all_tentacles(path.join("tests", "static", "tentacles.zip"), aiohttp_session=session) == 0
        yield
    _cleanup()


async def test_create_folder_tentacles_package(install_tentacles):
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
    generated_file_path = path.join(TENTACLES_PATH, TENTACLES_TRADING_PATH, "file.pyc")
    with open(generated_file_path, "w+") as generated_file:
        generated_file.write(random_content)
    # add generated python folder
    generated_folder_path = path.join(TENTACLES_PATH, TENTACLES_TRADING_PATH, "__pycache__")
    mkdir(generated_folder_path)

    # add gitignore file that should not be copied
    with open(path.join(TENTACLES_PATH, ".gitignore"), "w+") as ignored_file:
        ignored_file.write(random_content)

    # create folder to force folder merge
    mkdir(TENTACLE_PACKAGE)

    with open(path.join(TENTACLE_PACKAGE, "not_tentacle_file"), "w+") as rand_file:
        rand_file.write(random_content)

    mkdir(path.join(TENTACLE_PACKAGE, TENTACLES_TRADING_PATH))

    with open(path.join(TENTACLE_PACKAGE, TENTACLES_TRADING_PATH, "rnd"), "w+") as rand_file:
        rand_file.write(random_content)

    assert await create_tentacles_package(TENTACLE_PACKAGE, output_dir=".", in_zip=False) == 0
    assert path.exists(TENTACLE_PACKAGE)

    # random init file still here
    with open(path.join(TENTACLE_PACKAGE, TENTACLES_TRADING_PATH, "rnd")) as rand_file:
        assert random_content == rand_file.read()

    # file that is not in tentacles arch is copied since it's not in a zip
    assert path.exists(path.join(TENTACLE_PACKAGE, "not_tentacle_file"))

    # ignored file is not copied
    assert not path.exists(path.join(TENTACLE_PACKAGE, ".gitignore"))

    # generated file not copied
    assert not path.exists(path.join(TENTACLE_PACKAGE, TENTACLES_TRADING_PATH, "file.pyc"))

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

    # add every not in dev tentacles
    python_files = tuple(e[2] for e in walk(TENTACLE_PACKAGE) if any(i for i in e[2] if i.endswith(".py")))
    assert len(python_files) == 10


async def test_create_folder_tentacles_package_with_package_selector(install_tentacles):
    tentacle_path = path.join(TENTACLES_PATH, TENTACLES_TRADING_PATH, TENTACLES_TRADING_MODE_PATH)
    with open(path.join(tentacle_path, "daily_trading_mode", TENTACLE_METADATA), "w+") as metadata:
        new_metadata = {
            METADATA_VERSION: "1.2.0",
            METADATA_ORIGIN_PACKAGE: "OctoBot-Not-Quite-Default-Tentacles",
            METADATA_TENTACLES: ["DailyTradingMode"],
            METADATA_TENTACLES_REQUIREMENTS: [],
            METADATA_DEV_MODE: False
        }
        json.dump(new_metadata, metadata)

    assert await create_tentacles_package(TENTACLE_PACKAGE, output_dir=".", in_zip=False,
                                          exported_tentacles_package="OctoBot-Not-Quite-Default-Tentacles") == 0
    assert path.exists(TENTACLE_PACKAGE)

    # added daily_trading_mode
    trading_mode_tentacle_path = path.join(TENTACLE_PACKAGE, TENTACLES_TRADING_PATH, TENTACLES_TRADING_MODE_PATH)
    assert path.exists(path.join(trading_mode_tentacle_path, "daily_trading_mode"))
    assert path.exists(path.join(trading_mode_tentacle_path, "daily_trading_mode", "daily_trading_mode.py"))

    # did not add anything else then daily trading mode files and tests
    python_files = tuple(e[2] for e in walk(TENTACLE_PACKAGE) if any(i for i in e[2] if i.endswith(".py")))
    assert len(python_files) == 2


async def test_create_zipped_tentacles_package(install_tentacles):
    tentacle_package = "tentacle_package.zip"
    assert await create_tentacles_package(tentacle_package, output_dir=".") == 0
    assert path.exists(tentacle_package)
    assert not path.exists(TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)
    remove(tentacle_package)


async def test_create_cythonized_tentacles_package(install_tentacles):
    # remove evaluator and services tentacles to speed up compilation
    for folder in (TENTACLES_EVALUATOR_PATH, TENTACLES_SERVICES_PATH):
        rmtree(join(TENTACLES_PATH, folder))
    exchange_importer_path = join(TENTACLES_PATH,
                                  TENTACLES_BACKTESTING_PATH,
                                  TENTACLES_BACKTESTING_IMPORTERS_PATH,
                                  TENTACLES_BACKTESTING_THIRD_LEVEL_EXCHANGES_PATH,
                                  "generic_exchange_importer")
    # create artificial sub folder python file to ensure it will also get compiled
    mkdir(join(exchange_importer_path, "plop"))
    with open(join(exchange_importer_path, "plop", "file.py"), "w+") as file_w:
        file_w.write("plop=0")
    with open(join(exchange_importer_path, "plop", PYTHON_INIT_FILE), "w+") as file_w:
        file_w.write("")
    assert await create_tentacles_package(TENTACLE_PACKAGE, output_dir=".", in_zip=False, cythonize=True) == 0
    _check_compiled_tentacle(join(TENTACLE_PACKAGE,
                                  TENTACLES_BACKTESTING_PATH,
                                  TENTACLES_BACKTESTING_IMPORTERS_PATH,
                                  TENTACLES_BACKTESTING_THIRD_LEVEL_EXCHANGES_PATH,
                                  "generic_exchange_importer"),
                             3)
    _check_compiled_tentacle(join(TENTACLE_PACKAGE,
                                  TENTACLES_TRADING_PATH,
                                  TENTACLES_TRADING_MODE_PATH,
                                  "daily_trading_mode"),
                             2)


async def test_create_all_tentacles_bundle_cleaned_not_zipped_but_cythonized(install_tentacles):
    # remove evaluator and services tentacles to speed up compilation
    for folder in (TENTACLES_EVALUATOR_PATH, TENTACLES_SERVICES_PATH):
        rmtree(join(TENTACLES_PATH, folder))
    cleanup_test_env()
    assert await create_all_tentacles_bundle(TEST_EXPORT_DIR,
                                             in_zip=False,
                                             cythonize=True,
                                             should_remove_artifacts_after_use=True) == 0

    # test compiled content
    _check_compiled_tentacle(join(TEST_EXPORT_DIR, "generic_exchange_importer_1.2.0_bundle"), 2)
    _check_compiled_tentacle(join(TEST_EXPORT_DIR, "daily_trading_mode_1.2.0_bundle"), 2)

    # test should_remove_artifacts_after_use
    assert not os.path.isfile(os.path.join(TEST_EXPORT_DIR, "generic_exchange_importer"))
    assert not os.path.isfile(os.path.join(TEST_EXPORT_DIR, "daily_trading_mode"))

    # test bundle metadata
    assert_directory_has_file_with_content(os.path.join(TEST_EXPORT_DIR, "generic_exchange_importer_1.2.0_bundle"),
                                           "metadata.yaml",
                                           "name: generic_exchange_importer\ntype: tentacle\nversion: 1.2.0\n")
    cleanup_test_env()


async def test_create_all_tentacles_bundle_not_cleaned_and_zipped(install_tentacles):
    # remove evaluator and services tentacles to speed up compilation
    for folder in (TENTACLES_EVALUATOR_PATH, TENTACLES_SERVICES_PATH):
        rmtree(join(TENTACLES_PATH, folder))
    cleanup_test_env()
    assert await create_all_tentacles_bundle(TEST_EXPORT_DIR,
                                             in_zip=True,
                                             cythonize=False,
                                             should_remove_artifacts_after_use=False,
                                             should_zip_bundle=True) == 0

    # test not should_remove_artifacts_after_use
    assert os.path.isfile(os.path.join(TEST_EXPORT_DIR, "generic_exchange_importer.zip"))
    assert os.path.isfile(os.path.join(TEST_EXPORT_DIR, "daily_trading_mode.zip"))
    assert os.path.isfile(os.path.join(TEST_EXPORT_DIR, "generic_exchange_importer_1.2.0_bundle.zip"))
    assert os.path.isfile(os.path.join(TEST_EXPORT_DIR, "daily_trading_mode_1.2.0_bundle.zip"))
    assert not os.path.isdir(os.path.join(TEST_EXPORT_DIR, "generic_exchange_importer_1.2.0_bundle"))
    assert not os.path.isdir(os.path.join(TEST_EXPORT_DIR, "daily_trading_mode_1.2.0_bundle"))
    cleanup_test_env()

    assert await create_all_tentacles_bundle(TEST_EXPORT_DIR,
                                             in_zip=True,
                                             cythonize=False,
                                             should_remove_artifacts_after_use=False,
                                             should_zip_bundle=False) == 0

    # test not should_remove_artifacts_after_use
    assert os.path.isfile(os.path.join(TEST_EXPORT_DIR, "generic_exchange_importer.zip"))
    assert os.path.isfile(os.path.join(TEST_EXPORT_DIR, "daily_trading_mode.zip"))
    assert not os.path.isfile(os.path.join(TEST_EXPORT_DIR, "generic_exchange_importer_1.2.0_bundle.zip"))
    assert not os.path.isfile(os.path.join(TEST_EXPORT_DIR, "daily_trading_mode_1.2.0_bundle.zip"))
    assert os.path.isdir(os.path.join(TEST_EXPORT_DIR, "generic_exchange_importer_1.2.0_bundle"))
    assert os.path.isdir(os.path.join(TEST_EXPORT_DIR, "daily_trading_mode_1.2.0_bundle"))
    cleanup_test_env()


def assert_directory_has_file_with_content(directory_to_check, expected_file, expected_content):
    with open(os.path.join(directory_to_check, expected_file), "r") as file_to_test:
        assert file_to_test.read() == expected_content


def cleanup_test_env():
    if os.path.exists(TEST_EXPORT_DIR):
        rmtree(TEST_EXPORT_DIR)
    if os.path.exists(DEFAULT_EXPORT_DIR):
        rmtree(DEFAULT_EXPORT_DIR)


def _check_compiled_tentacle(tentacle_path, expected_dir_count):
    dir_count = 0
    has_compiled_file = False
    for entry in scandir(tentacle_path):
        if entry.is_file():
            if entry.name.endswith(".py"):
                assert entry.name == PYTHON_INIT_FILE
            elif not (entry.name.endswith(".json") or entry.name.endswith(".yaml")):
                assert entry.name.endswith(".pyd") or entry.name.endswith(".so")
                assert getsize(entry) >= 100
                has_compiled_file = True
        elif entry.is_dir():
            dir_count += 1
    assert has_compiled_file
    assert dir_count == expected_dir_count


def _cleanup():
    if exists(TENTACLES_PATH):
        TentaclesSetupManager.delete_tentacles_arch(force=True)
    if exists(TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER):
        rmtree(TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)
    if exists(TENTACLE_PACKAGE):
        rmtree(TENTACLE_PACKAGE)
