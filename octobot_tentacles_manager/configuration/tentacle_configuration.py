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
import os.path as path
import shutil 

import octobot_tentacles_manager.configuration as configuration
import octobot_tentacles_manager.constants as constants
import octobot_tentacles_manager.loaders as loaders


def get_config(klass) -> dict:
    return configuration.read_config(_get_config_file_path(klass))


def update_config(klass, config_update) -> None:
    config_file = _get_config_file_path(klass)
    current_config = configuration.read_config(config_file)
    # only update values in config update not to erase values in root config (might not be editable)
    current_config.update(config_update)
    configuration.write_config(config_file, current_config)


def factory_reset_config(klass) -> None:
    reference_config_path = path.join(_get_reference_config_path(klass), _get_config_file_name(klass))
    shutil.copy(reference_config_path, _get_config_file_path(klass))


def get_config_schema_path(klass) -> str:
    return path.join(_get_reference_config_path(klass), f"{klass.get_name()}{constants.CONFIG_SCHEMA_EXT}")


def _get_config_file_path(klass) -> str:
    return path.join(constants.USER_TENTACLE_SPECIFIC_CONFIG_PATH, _get_config_file_name(klass))


def _get_reference_config_path(klass) -> str:
    return path.join(loaders.get_tentacle_module_path(klass), constants.TENTACLE_CONFIG)


def _get_config_file_name(klass) -> str:
    return f"{klass.get_name()}{constants.CONFIG_EXT}"
