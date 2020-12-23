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
import os

import pytest
import yaml

import octobot_tentacles_manager.models as models
import octobot_tentacles_manager.exporters as exporters
import octobot_tentacles_manager.util as util
import octobot_tentacles_manager.constants as constants
from tests.api import install_tentacles

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_each_tentacle_bundle_exporter(install_tentacles):
    for tentacle in util.load_tentacle_with_metadata(constants.TENTACLES_PATH):
        tentacle_package = models.TentaclePackage()
        await exporters.TentacleExporter(artifact=tentacle, should_zip=True,
                                         tentacles_folder=constants.TENTACLES_PATH).export()
        tentacle_package.add_artifact(tentacle)
        await exporters.TentacleBundleExporter(
            artifact=tentacle_package,
            tentacles_folder=constants.TENTACLES_PATH).export()

    # check files count
    output_files = os.listdir(constants.DEFAULT_EXPORT_DIR)
    assert len(output_files) == 20
    assert "daily_trading_mode.zip" in output_files
    assert "generic_exchange_importer_1.2.0_package" in output_files
    assert "other_instant_fluctuations_evaluator_1.2.0_package" in output_files
    assert "mixed_strategies_evaluator.zip" in output_files
    assert "mixed_strategies_evaluator" not in output_files


async def test_all_tentacle_bundle_exporter(install_tentacles):
    tentacle_package = models.TentaclePackage()
    for tentacle in util.load_tentacle_with_metadata(constants.TENTACLES_PATH):
        await exporters.TentacleExporter(artifact=tentacle, should_zip=True,
                                         tentacles_folder=constants.TENTACLES_PATH).export()
        tentacle_package.add_artifact(tentacle)
    await exporters.TentacleBundleExporter(
        artifact=tentacle_package,
        tentacles_folder=constants.TENTACLES_PATH,
        should_remove_artifacts_after_use=True).export()

    # check files count
    output_files = os.listdir(constants.DEFAULT_EXPORT_DIR)
    assert len(output_files) == 1
    exported_bundle_path = os.path.join(constants.DEFAULT_EXPORT_DIR, output_files[0])
    output_files = os.listdir(exported_bundle_path)
    assert len(output_files) == 11
    assert "daily_trading_mode.zip" in output_files
    assert "generic_exchange_importer_1.2.0_package" not in output_files
    assert "other_instant_fluctuations_evaluator_1.2.0_package" not in output_files
    assert "mixed_strategies_evaluator.zip" in output_files
    assert "mixed_strategies_evaluator" not in output_files
    assert constants.ARTIFACT_METADATA_FILE in output_files

    # test multiple tentacle bundle metadata
    with open(os.path.join(exported_bundle_path, constants.ARTIFACT_METADATA_FILE)) as metadata_file:
        metadata_content = yaml.load(metadata_file.read())
        assert metadata_content[constants.ARTIFACT_METADATA_ARTIFACT_TYPE] == "tentacle_package"
        assert len(metadata_content[constants.ARTIFACT_METADATA_ARTIFACTS]) == 10
        assert "forum_evaluator" in metadata_content[constants.ARTIFACT_METADATA_ARTIFACTS]
