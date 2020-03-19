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
from octobot_tentacles_manager.configuration.tentacle_configuration import update_config, get_config, \
    factory_reset_config, get_config_schema_path
from octobot_tentacles_manager.configuration.tentacles_setup_configuration import TentaclesSetupConfiguration
from octobot_tentacles_manager.constants import USER_TENTACLE_CONFIG_FILE_PATH


async def get_tentacles_setup_config(config_path=USER_TENTACLE_CONFIG_FILE_PATH) -> TentaclesSetupConfiguration:
    setup_config = TentaclesSetupConfiguration(config_path=config_path)
    await setup_config.read_config()
    return setup_config


def is_tentacle_activated_in_tentacles_setup_config(tentacles_setup_config, klass_name) -> bool:
    return tentacles_setup_config.tentacles_activation[klass_name]


async def update_tentacle_config(tentacle_class: object, config_data: dict) -> None:
    await update_config(tentacle_class, config_data)


async def get_tentacle_config(klass) -> dict:
    return await get_config(klass)


def factory_tentacle_reset_config(klass) -> None:
    return factory_reset_config(klass)


def get_tentacle_config_schema_path(klass) -> str:
    return get_config_schema_path(klass)
