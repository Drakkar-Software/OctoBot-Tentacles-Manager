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

from octobot_tentacles_manager.api import configurator
from octobot_tentacles_manager.api import updater
from octobot_tentacles_manager.api import loader
from octobot_tentacles_manager.api import inspector
from octobot_tentacles_manager.api import uninstaller
from octobot_tentacles_manager.api import creator
from octobot_tentacles_manager.api import installer
from octobot_tentacles_manager.api import util
from octobot_tentacles_manager.api import uploader

from octobot_tentacles_manager.api.util import (
    manage_tentacles,
)

from octobot_tentacles_manager.api.uploader import (
    upload_file_or_folder,
    upload_file_to_nexus,
    upload_folder_to_nexus,
    upload_file_or_folder_to_nexus,
    upload_file_to_s3,
    upload_folder_to_s3,
    upload_file_or_folder_to_s3,
)

from octobot_tentacles_manager.api.configurator import (
    get_tentacles_setup_config,
    create_tentacles_setup_config_with_tentacles,
    is_tentacle_activated_in_tentacles_setup_config,
    get_class_from_name_with_activated_required_tentacles,
    get_tentacles_activation,
    get_registered_tentacle_packages,
    unregister_tentacle_packages,
    update_activation_configuration,
    save_tentacles_setup_configuration,
    get_activated_tentacles,
    update_tentacle_config,
    get_tentacle_config,
    factory_tentacle_reset_config,
    get_tentacle_config_schema_path,
    get_compiled_tentacles_url,
    ensure_setup_configuration,
)
from octobot_tentacles_manager.api.updater import (
    update_all_tentacles,
    update_tentacles,
)
from octobot_tentacles_manager.api.loader import (
    load_tentacles,
    reload_tentacle_info,
    are_tentacles_up_to_date,
)
from octobot_tentacles_manager.api.inspector import (
    get_installed_tentacles_modules,
    get_tentacle_group,
    get_tentacle_version,
    get_tentacle_origin_package,
    get_tentacle_module_name,
    get_tentacle_resources_path,
    get_tentacle_documentation_path,
    check_tentacle_version,
)
from octobot_tentacles_manager.api.uninstaller import (
    uninstall_all_tentacles,
    uninstall_tentacles,
)
from octobot_tentacles_manager.api.creator import (
    start_tentacle_creator,
    create_tentacles_package,
    create_all_tentacles_bundle,
)
from octobot_tentacles_manager.api.installer import (
    install_all_tentacles,
    install_tentacles,
    install_single_tentacle,
    repair_installation,
)

__all__ = [
    "get_tentacles_setup_config",
    "create_tentacles_setup_config_with_tentacles",
    "is_tentacle_activated_in_tentacles_setup_config",
    "get_class_from_name_with_activated_required_tentacles",
    "get_tentacles_activation",
    "get_registered_tentacle_packages",
    "unregister_tentacle_packages",
    "update_activation_configuration",
    "save_tentacles_setup_configuration",
    "get_activated_tentacles",
    "update_tentacle_config",
    "get_tentacle_config",
    "factory_tentacle_reset_config",
    "get_tentacle_config_schema_path",
    "get_compiled_tentacles_url",
    "ensure_setup_configuration",
    "update_all_tentacles",
    "update_tentacles",
    "load_tentacles",
    "reload_tentacle_info",
    "are_tentacles_up_to_date",
    "get_installed_tentacles_modules",
    "get_tentacle_group",
    "get_tentacle_version",
    "get_tentacle_origin_package",
    "get_tentacle_module_name",
    "get_tentacle_resources_path",
    "get_tentacle_documentation_path",
    "check_tentacle_version",
    "uninstall_all_tentacles",
    "uninstall_tentacles",
    "start_tentacle_creator",
    "create_tentacles_package",
    "install_all_tentacles",
    "install_tentacles",
    "install_single_tentacle",
    "repair_installation",
    "manage_tentacles",
    "create_all_tentacles_bundle",
    "upload_file_or_folder",
    "upload_file_to_nexus",
    "upload_folder_to_nexus",
    "upload_file_or_folder_to_nexus",
    "upload_file_to_s3",
    "upload_folder_to_s3",
    "upload_file_or_folder_to_s3",
]
