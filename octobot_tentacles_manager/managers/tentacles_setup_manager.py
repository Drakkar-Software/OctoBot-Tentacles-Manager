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
from asyncio import gather
from os import remove
from os.path import join, exists
from shutil import rmtree

from octobot_commons.logging.logging_util import get_logger
from octobot_tentacles_manager.configuration.tentacles_setup_configuration import TentaclesSetupConfiguration
from octobot_tentacles_manager.constants import USER_TENTACLE_SPECIFIC_CONFIG_PATH, PYTHON_INIT_FILE, \
    TENTACLES_FOLDERS_ARCH, DEFAULT_TENTACLE_CONFIG, TENTACLES_PATH, USER_TENTACLE_CONFIG_PATH, \
    TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR, DEFAULT_BOT_PATH
from octobot_tentacles_manager.managers.tentacles_init_files_manager import find_or_create_module_init_file, \
    get_module_init_file_content
from octobot_tentacles_manager.util.file_util import find_or_create
from octobot_tentacles_manager.util.tentacle_explorer import load_tentacle_with_metadata


class TentaclesSetupManager:

    def __init__(self, tentacle_setup_root_path, bot_installation_path=DEFAULT_BOT_PATH):
        self.tentacle_setup_root_path = tentacle_setup_root_path
        self.default_tentacle_config = DEFAULT_TENTACLE_CONFIG
        self.bot_installation_path = bot_installation_path

    async def refresh_user_tentacles_setup_config_file(self):
        available_tentacle = await load_tentacle_with_metadata(self.tentacle_setup_root_path)
        tentacle_setup_config = TentaclesSetupConfiguration(bot_installation_path=self.bot_installation_path)
        await tentacle_setup_config.read_config()
        await tentacle_setup_config.fill_tentacle_config(available_tentacle, self.default_tentacle_config)
        await tentacle_setup_config.save_config()

    async def create_missing_tentacles_arch(self):
        # tentacle user config folder
        await find_or_create(join(self.bot_installation_path, USER_TENTACLE_SPECIFIC_CONFIG_PATH))
        # tentacles folder
        found_existing_installation = not await find_or_create(self.tentacle_setup_root_path)
        # tentacle main python init file
        await find_or_create(join(self.tentacle_setup_root_path, PYTHON_INIT_FILE), False,
                             get_module_init_file_content(TENTACLES_FOLDERS_ARCH.keys()))
        # tentacle inner architecture
        await TentaclesSetupManager._tentacle_arch_operation(self.tentacle_setup_root_path,
                                                             TENTACLES_FOLDERS_ARCH,
                                                             self._create_missing_files_and_folders,
                                                             find_or_create)
        await self._create_missing_files_and_folders(self.tentacle_setup_root_path, TENTACLES_FOLDERS_ARCH)
        return found_existing_installation

    async def remove_tentacle_arch_init_files(self):
        await TentaclesSetupManager._remove_tentacles_arch_init_file(self.tentacle_setup_root_path, None)
        await TentaclesSetupManager._tentacle_arch_operation(self.tentacle_setup_root_path,
                                                             TENTACLES_FOLDERS_ARCH,
                                                             self._remove_tentacles_arch_init_file,
                                                             self._remove_tentacles_arch_init_file)

    @staticmethod
    def cleanup_temp_dirs():
        if exists(TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR):
            rmtree(TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR)

    @staticmethod
    def is_tentacles_arch_valid(verbose=True, raises=False) -> bool:
        try:
            import tentacles
            return exists(TENTACLES_PATH)
        except (ImportError, SyntaxError) as e:
            if verbose:
                get_logger(TentaclesSetupManager.__name__).exception(e, True, f"Error when importing tentacles: {e}")
            if raises:
                raise e
            return False

    @staticmethod
    def delete_tentacles_arch(force=False, raises=False,
                              with_user_config=False, bot_installation_path=DEFAULT_BOT_PATH):
        if TentaclesSetupManager.is_tentacles_arch_valid(verbose=False, raises=raises) \
          or (force and exists(join(bot_installation_path, TENTACLES_PATH))):
            rmtree(join(bot_installation_path, TENTACLES_PATH))
        if with_user_config and exists(join(bot_installation_path, USER_TENTACLE_CONFIG_PATH)):
            rmtree(join(bot_installation_path, USER_TENTACLE_CONFIG_PATH))

    @staticmethod
    def get_available_tentacles_repos():
        # TODO: add advanced tentacles repos
        return [TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR]

    @staticmethod
    async def _tentacle_arch_operation(root_folder, files_arch, branch_func, leaf_func):
        sub_dir_to_handle_coroutines = []
        for root, modules in files_arch.items():
            current_root = join(root_folder, root)
            await branch_func(current_root, modules)
            if isinstance(modules, dict):
                sub_dir_to_handle_coroutines.append(
                    TentaclesSetupManager._tentacle_arch_operation(current_root, modules, branch_func, leaf_func))
            elif leaf_func is not None:
                sub_dir_to_handle_coroutines += [leaf_func(join(current_root, directory))
                                                 for directory in modules]
        await gather(*sub_dir_to_handle_coroutines)

    @staticmethod
    async def _create_missing_files_and_folders(current_root, modules):
        await find_or_create(current_root)
        # create python init file
        await find_or_create_module_init_file(current_root, modules)

    @staticmethod
    async def _remove_tentacles_arch_init_file(current_root, _=None):
        potential_init_file = join(current_root, PYTHON_INIT_FILE)
        if exists(potential_init_file):
            remove(potential_init_file)
