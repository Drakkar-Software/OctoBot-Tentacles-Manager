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

import octobot_commons.tentacles_management as tentacles_management

import octobot_tentacles_manager.api as api
import octobot_tentacles_manager.configuration as configuration
import octobot_tentacles_manager.constants as constants
import octobot_tentacles_manager.util as util


async def ensure_setup_configuration(tentacle_path=constants.TENTACLES_PATH, bot_path=constants.DEFAULT_BOT_PATH,
                                     bot_install_dir=constants.DEFAULT_BOT_INSTALL_DIR) -> None:
    if not path.exists(path.join(bot_path, constants.USER_REFERENCE_TENTACLE_CONFIG_FILE_PATH)):
        await api.repair_installation(tentacle_path, bot_path, bot_install_dir, verbose=False)


def get_tentacles_setup_config(
        config_path=constants.USER_REFERENCE_TENTACLE_CONFIG_FILE_PATH) -> configuration.TentaclesSetupConfiguration:
    setup_config = configuration.TentaclesSetupConfiguration(config_path=config_path)
    setup_config.read_config()
    return setup_config


def create_tentacles_setup_config_with_tentacles(*tentacles_classes):
    setup_config = configuration.TentaclesSetupConfiguration()
    setup_config.from_activated_tentacles_classes(*tentacles_classes)
    return setup_config


def is_tentacle_activated_in_tentacles_setup_config(tentacles_setup_config: configuration.TentaclesSetupConfiguration,
                                                    klass_name: str, default_value=False, raise_errors=False) -> bool:
    try:
        return tentacles_setup_config.is_tentacle_activated(klass_name)
    except KeyError as e:
        if raise_errors:
            raise e
        return default_value


def get_class_from_name_with_activated_required_tentacles(name: str,
                                                          parent_class,
                                                          tentacles_setup_config: configuration.TentaclesSetupConfiguration,
                                                          with_class_method=None):
    for subclass in tentacles_management.get_all_classes_from_parent(parent_class):
        # Filter sub classes to only use the one that is appropriate to the given name and that has its
        # tentacles requirements activated (identified by REQUIRED_ACTIVATED_TENTACLES iterable class attribute).
        if subclass.get_name() == name and \
                tentacles_setup_config is not None and \
                all(is_tentacle_activated_in_tentacles_setup_config(tentacles_setup_config, required_tentacle.__name__)
                    for required_tentacle in subclass.REQUIRED_ACTIVATED_TENTACLES):
            if with_class_method is None or getattr(subclass, with_class_method)():
                return subclass
    return None


def get_tentacles_activation(tentacles_setup_config: configuration.TentaclesSetupConfiguration) -> dict:
    return tentacles_setup_config.tentacles_activation


def get_tentacles_config_folder(tentacles_setup_config: configuration.TentaclesSetupConfiguration) -> str:
    return tentacles_setup_config.get_config_folder()


def get_registered_tentacle_packages(tentacles_setup_config: configuration.TentaclesSetupConfiguration) -> dict:
    return tentacles_setup_config.registered_tentacles


def unregister_tentacle_packages(tentacles_setup_config: configuration.TentaclesSetupConfiguration,
                                 package_name: str) -> dict:
    return tentacles_setup_config.unregister_tentacles_package(package_name)


def update_activation_configuration(tentacles_setup_config: configuration.TentaclesSetupConfiguration,
                                    new_config: dict, deactivate_others: bool, add_missing_elements=False) \
        -> bool:
    return tentacles_setup_config.update_activation_configuration(new_config, deactivate_others, add_missing_elements)


def save_tentacles_setup_configuration(tentacles_setup_config: configuration.TentaclesSetupConfiguration) -> None:
    tentacles_setup_config.save_config()


def get_activated_tentacles(tentacles_setup_config: configuration.TentaclesSetupConfiguration) -> list:
    return [tentacle_class
            for tentacle_classes in tentacles_setup_config.tentacles_activation.values()
            for tentacle_class, activated in tentacle_classes.items()
            if activated]


def update_tentacle_config(tentacles_setup_config: configuration.TentaclesSetupConfiguration,
                           tentacle_class: object, config_data: dict) -> None:
    configuration.update_config(tentacles_setup_config, tentacle_class, config_data)


def get_tentacle_config(tentacles_setup_config: configuration.TentaclesSetupConfiguration, klass) -> dict:
    return configuration.get_config(tentacles_setup_config, klass)


def factory_tentacle_reset_config(tentacles_setup_config: configuration.TentaclesSetupConfiguration, klass) -> None:
    return configuration.factory_reset_config(tentacles_setup_config, klass)


def get_tentacle_config_schema_path(klass) -> str:
    return configuration.get_config_schema_path(klass)


def get_compiled_tentacles_url(base_url, version) -> str:
    return f"{base_url}{util.get_local_arch_download_path()}/{version}.zip"
