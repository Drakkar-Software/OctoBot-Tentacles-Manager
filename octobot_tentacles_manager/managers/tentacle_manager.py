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
from os import listdir
from os.path import join, isfile, exists
from shutil import copyfile, rmtree, copytree

from octobot_commons.logging.logging_util import get_logger
from octobot_tentacles_manager.constants import USER_TENTACLE_SPECIFIC_CONFIG_PATH, CONFIG_SCHEMA_EXT, \
    TENTACLE_CONFIG, CONFIG_EXT
from octobot_tentacles_manager.managers.tentacles_init_files_manager import create_tentacle_init_file_if_necessary
from octobot_tentacles_manager.util.file_util import find_or_create


class TentacleManager:

    def __init__(self, tentacle):
        self.tentacle = tentacle
        self.target_tentacle_path = None

    async def install_tentacle(self, tentacle_path):
        self.target_tentacle_path = join(tentacle_path, self.tentacle.tentacle_type.to_path())
        tentacle_module_path = join(self.target_tentacle_path, self.tentacle.name)
        await self._update_tentacle_folder(tentacle_path)
        await create_tentacle_init_file_if_necessary(tentacle_module_path, self.tentacle)
        self._import_tentacle_config_if_any(tentacle_module_path)

    async def uninstall_tentacle(self):
        rmtree(join(self.tentacle.tentacle_path, self.tentacle.name))

    @staticmethod
    def find_tentacles_missing_requirements(tentacle, version_by_modules):
        # check if requirement is in tentacles to be installed in this call
        return {
            requirement: version
            for requirement, version in tentacle.extract_tentacle_requirements()
            if not TentacleManager.is_requirement_satisfied(requirement, version, tentacle, version_by_modules)
        }

    @staticmethod
    def is_requirement_satisfied(requirement, version, tentacle, version_by_modules):
        satisfied = False
        if requirement in version_by_modules:
            available = version_by_modules[requirement]
            if version is None:
                satisfied = True
            elif version != available:
                get_logger(TentacleManager.__name__).\
                    error(f"Incompatible tentacle version requirement for "
                          f"{tentacle.name}: requires {version}, installed: "
                          f"{available}. This tentacle might not work as expected")
                satisfied = True
        return satisfied

    async def _update_tentacle_folder(self, tentacle_path):
        reference_tentacle_path = join(self.tentacle.tentacle_path, self.tentacle.name)
        target_tentacle_path = join(tentacle_path, self.tentacle.tentacle_type.to_path(), self.tentacle.name)
        await find_or_create(target_tentacle_path)
        for tentacle_file in listdir(reference_tentacle_path):
            file_or_dir = join(reference_tentacle_path, tentacle_file)
            target_file_or_dir = join(target_tentacle_path, tentacle_file)
            if isfile(file_or_dir):
                copyfile(file_or_dir, target_file_or_dir)
            else:
                if exists(target_file_or_dir):
                    rmtree(target_file_or_dir)
                copytree(file_or_dir, target_file_or_dir)

    @staticmethod
    def _import_tentacle_config_if_any(tentacle_module_path, replace=False):
        target_tentacle_config_path = join(tentacle_module_path, TENTACLE_CONFIG)
        for config_file in listdir(target_tentacle_config_path):
            if config_file.endswith(CONFIG_EXT) and not config_file.endswith(CONFIG_SCHEMA_EXT):
                target_user_path = join(USER_TENTACLE_SPECIFIC_CONFIG_PATH, config_file)
                if replace or not exists(target_user_path):
                    copyfile(join(target_tentacle_config_path, config_file), target_user_path)
