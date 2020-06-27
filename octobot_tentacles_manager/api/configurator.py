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
from os.path import exists, join

from octobot_tentacles_manager.api.installer import repair_installation
from octobot_tentacles_manager.configuration.tentacle_configuration import get_config, \
    factory_reset_config, get_config_schema_path, update_config
from octobot_tentacles_manager.configuration.tentacles_setup_configuration import TentaclesSetupConfiguration
from octobot_tentacles_manager.constants import USER_TENTACLE_CONFIG_FILE_PATH, DEFAULT_BOT_PATH, TENTACLES_PATH, \
    DEFAULT_BOT_INSTALL_DIR


async def ensure_setup_configuration(tentacle_path=TENTACLES_PATH, bot_path=DEFAULT_BOT_PATH,
                                     bot_install_dir=DEFAULT_BOT_INSTALL_DIR) -> None:
    if not exists(join(bot_path, USER_TENTACLE_CONFIG_FILE_PATH)):
        await repair_installation(tentacle_path, bot_path, bot_install_dir, verbose=False)


def get_tentacles_setup_config(config_path=USER_TENTACLE_CONFIG_FILE_PATH) -> TentaclesSetupConfiguration:
    setup_config = TentaclesSetupConfiguration(config_path=config_path)
    setup_config.read_config()
    return setup_config


def create_tentacles_setup_config_with_tentacles(*tentacles_classes):
    setup_config = TentaclesSetupConfiguration()
    setup_config.from_activated_tentacles_classes(*tentacles_classes)
    return setup_config


def is_tentacle_activated_in_tentacles_setup_config(tentacles_setup_config, klass_name,
                                                    default_value=False, raise_errors=False) -> bool:
    try:
        return tentacles_setup_config.is_tentacle_activated(klass_name)
    except KeyError as e:
        if raise_errors:
            raise e
        return default_value


def get_tentacles_activation(tentacles_setup_config) -> dict:
    return tentacles_setup_config.tentacles_activation


def get_registered_tentacle_packages(tentacles_setup_config) -> dict:
    return tentacles_setup_config.registered_tentacles


def unregister_tentacle_packages(tentacles_setup_config, package_name) -> dict:
    return tentacles_setup_config.unregister_tentacles_package(package_name)


def update_activation_configuration(tentacles_setup_config, new_config, deactivate_others, add_missing_elements=False) \
        -> bool:
    return tentacles_setup_config.update_activation_configuration(new_config, deactivate_others, add_missing_elements)


def save_tentacles_setup_configuration(tentacles_setup_config) -> None:
    tentacles_setup_config.save_config()


def get_activated_tentacles(tentacles_setup_config) -> list:
    return [tentacle_class
            for tentacle_classes in tentacles_setup_config.tentacles_activation.values()
            for tentacle_class, activated in tentacle_classes.items()
            if activated]


def update_tentacle_config(tentacle_class: object, config_data: dict) -> None:
    update_config(tentacle_class, config_data)


def get_tentacle_config(klass) -> dict:
    return get_config(klass)


def factory_tentacle_reset_config(klass) -> None:
    return factory_reset_config(klass)


def get_tentacle_config_schema_path(klass) -> str:
    return get_config_schema_path(klass)
