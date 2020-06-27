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
from octobot_tentacles_manager.constants import USER_TENTACLE_CONFIG_PATH, USER_TENTACLE_SPECIFIC_CONFIG_PATH, \
    USER_TENTACLE_CONFIG_FILE_PATH, TENTACLES_PATH, DEFAULT_BOT_PATH, UNKNOWN_TENTACLES_PACKAGE_LOCATION
from octobot_tentacles_manager.workers.install_worker import InstallWorker
from octobot_tentacles_manager.models.tentacle_factory import TentacleFactory
from octobot_tentacles_manager.workers.update_worker import UpdateWorker

# All test coroutines will be treated as marked.
from octobot_tentacles_manager.models.tentacle import Tentacle
from octobot_tentacles_manager.util.tentacle_fetching import fetch_and_extract_tentacles

pytestmark = pytest.mark.asyncio

temp_dir = "temp_tests"


async def test_update_two_tentacles():
    _cleanup()
    _enable_loggers()
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
    install_worker = InstallWorker(temp_dir, TENTACLES_PATH, DEFAULT_BOT_PATH, False, None)
    install_worker.tentacles_setup_manager.default_tentacle_config = \
        path.join("tests", "static", "default_tentacle_config.json")
    await install_worker.process(["instant_fluctuations_evaluator",
                                  "generic_exchange_importer",
                                  "text_analysis"])
    rmtree(temp_dir)

    # edit instant_fluctuations_evaluator config to ensure file is not replaced
    config_path = path.join(USER_TENTACLE_SPECIFIC_CONFIG_PATH, "InstantFluctuationsEvaluator.json")
    with open(config_path, "r+") as config_f:
        new_content = f"{config_f.read()},"
        config_f.write(",")
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "update_tentacles.zip"), None)
    update_worker = UpdateWorker(temp_dir, TENTACLES_PATH, DEFAULT_BOT_PATH, False, None)
    update_worker.tentacles_setup_manager.default_tentacle_config = \
        path.join("tests", "static", "default_tentacle_config.json")
    assert await update_worker.process(["instant_fluctuations_evaluator", "generic_exchange_importer"]) == 0

    # ensure instant_fluctuations_evaluator file is not replaced
    with open(config_path, "r") as config_f:
        assert new_content == config_f.read()

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
                'OctoBot-Default-Tentacles': UNKNOWN_TENTACLES_PACKAGE_LOCATION
            },
            'tentacle_activation': {
                'Backtesting': {
                    'GenericExchangeDataImporter': True
                },
                'Evaluator': {
                    'InstantFluctuationsEvaluator': True,
                    'TextAnalysis': True
                }
            }
        }

    # check updated versions
    factory = TentacleFactory("tentacles")
    from tentacles.Evaluator.RealTime import instant_fluctuations_evaluator
    ife_tentacle_data = await factory.create_and_load_tentacle_from_module(instant_fluctuations_evaluator)
    assert ife_tentacle_data.version == "1.3.0"
    # not updated because update version is "1.1.9"
    import tentacles.Backtesting.importers.exchanges.generic_exchange_importer as gei
    gei_tentacle_data = await factory.create_and_load_tentacle_from_module(gei)
    assert gei_tentacle_data.version == "1.2.0"
    import tentacles.Evaluator.Util.text_analysis
    ta_tentacle_data = await factory.create_and_load_tentacle_from_module(tentacles.Evaluator.Util.text_analysis)
    assert ta_tentacle_data.version == "1.2.0"
    _cleanup()


async def test_update_all_tentacles():
    _cleanup()
    _enable_loggers()
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "tentacles.zip"), None)
    install_worker = InstallWorker(temp_dir, TENTACLES_PATH, DEFAULT_BOT_PATH, False, None)
    install_worker.tentacles_setup_manager.default_tentacle_config = \
        path.join("tests", "static", "default_tentacle_config.json")
    await install_worker.process()
    rmtree(temp_dir)
    await fetch_and_extract_tentacles(temp_dir, path.join("tests", "static", "update_tentacles.zip"), None)
    update_worker = UpdateWorker(temp_dir, TENTACLES_PATH, DEFAULT_BOT_PATH, False, None)
    update_worker.tentacles_setup_manager.default_tentacle_config = \
        path.join("tests", "static", "default_tentacle_config.json")
    assert await update_worker.process() == 0

    # check updated versions
    factory = TentacleFactory(TENTACLES_PATH)
    from tentacles.Evaluator.RealTime import instant_fluctuations_evaluator
    ife_tentacle_data = await factory.create_and_load_tentacle_from_module(instant_fluctuations_evaluator)
    assert ife_tentacle_data.version == "1.3.0"
    import tentacles.Backtesting.importers.exchanges.generic_exchange_importer as gei
    gei_tentacle_data = await factory.create_and_load_tentacle_from_module(gei)
    # not updated because update version is "1.1.9"
    assert gei_tentacle_data.version == "1.2.0"
    import tentacles.Evaluator.Util.text_analysis
    ta_tentacle_data = await factory.create_and_load_tentacle_from_module(tentacles.Evaluator.Util.text_analysis)
    assert ta_tentacle_data.version == "1.3.0"
    import tentacles.Trading.Mode.daily_trading_mode as dtm
    dtm_tentacle_data = await factory.create_and_load_tentacle_from_module(dtm)
    assert dtm_tentacle_data.version == "1.3.0"
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
