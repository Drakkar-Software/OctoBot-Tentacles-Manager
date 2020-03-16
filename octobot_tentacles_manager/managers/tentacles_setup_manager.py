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
from os.path import join, isfile, exists
from shutil import rmtree

import aiofiles

from octobot_commons.logging.logging_util import get_logger
from octobot_tentacles_manager.configuration.tentacles_setup_configuration import TentaclesSetupConfiguration
from octobot_tentacles_manager.constants import USER_TENTACLE_SPECIFIC_CONFIG_PATH, PYTHON_INIT_FILE, \
    TENTACLES_FOLDERS_ARCH, DEFAULT_TENTACLE_CONFIG, TENTACLES_PATH, USER_TENTACLE_CONFIG_PATH, \
    TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR
from octobot_tentacles_manager.util.file_util import find_or_create
from octobot_tentacles_manager.util.tentacle_explorer import load_tentacle_with_metadata


class TentaclesSetupManager:

    def __init__(self, tentacle_path):
        self.tentacle_path = tentacle_path
        self.default_tentacle_config = DEFAULT_TENTACLE_CONFIG

    async def refresh_tentacles_config_file(self):
        available_tentacle = await load_tentacle_with_metadata(self.tentacle_path)
        tentacle_setup_config = TentaclesSetupConfiguration()
        await tentacle_setup_config.read_config()
        await tentacle_setup_config.fill_tentacle_config(available_tentacle, self.default_tentacle_config)
        await tentacle_setup_config.save_config()

    async def create_missing_tentacles_arch(self):
        # tentacle user config folder
        await find_or_create(USER_TENTACLE_SPECIFIC_CONFIG_PATH)
        # tentacles folder
        found_existing_installation = not await find_or_create(self.tentacle_path)
        # tentacle mail python init file
        await find_or_create(join(self.tentacle_path, PYTHON_INIT_FILE), False,
                             self.get_module_init_file_content(TENTACLES_FOLDERS_ARCH.keys()))
        # tentacle inner architecture
        await self._rec_create_missing_files(self.tentacle_path, TENTACLES_FOLDERS_ARCH)
        return found_existing_installation

    @staticmethod
    async def update_tentacle_type_init_file(tentacle, target_tentacle_path, remove_import=False):
        init_content = ""
        init_file = join(target_tentacle_path, PYTHON_INIT_FILE)
        if isfile(init_file):
            # load import file
            async with aiofiles.open(init_file, "r") as init_file_r:
                init_content = await init_file_r.read()
        if remove_import:
            # remove import line
            if init_content:
                to_remove_line = f"{TentaclesSetupManager._get_single_module_init_line(tentacle)}\n"
                if to_remove_line in init_content:
                    init_content = init_content.replace(to_remove_line, "")
                    async with aiofiles.open(init_file, "w+") as init_file_w:
                        await init_file_w.write(init_content)
        elif tentacle.name not in init_content:
            # add import line
            init_content = f"{init_content}{TentaclesSetupManager._get_single_module_init_line(tentacle)}\n"
            async with aiofiles.open(init_file, "w+") as init_file_w:
                await init_file_w.write(init_content)

    @staticmethod
    def is_tentacles_arch_valid(verbose=True) -> bool:
        try:
            import tentacles
            return exists(TENTACLES_PATH)
        except (ImportError, SyntaxError) as e:
            if verbose:
                get_logger(TentaclesSetupManager.__name__).exception(e, True, f"Error when importing tentacles: {e}")
            return False

    @staticmethod
    def delete_tentacles_arch():
        if TentaclesSetupManager.is_tentacles_arch_valid(verbose=False):
            rmtree(TENTACLES_PATH)
        if exists(USER_TENTACLE_CONFIG_PATH):
            rmtree(USER_TENTACLE_CONFIG_PATH)

    @staticmethod
    def get_available_tentacles_repos():
        # TODO: add advanced tentacles repos
        return [TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR]

    @staticmethod
    async def _rec_create_missing_files(root_folder, files_arch):
        sub_dir_to_create_coroutines = []
        for root, subdir in files_arch.items():
            current_root = join(root_folder, root)
            await find_or_create(current_root)
            # create python init file
            await find_or_create(join(current_root, PYTHON_INIT_FILE), False,
                                 TentaclesSetupManager.get_module_init_file_content(subdir))
            if isinstance(subdir, dict):
                sub_dir_to_create_coroutines.append(
                    TentaclesSetupManager._rec_create_missing_files(current_root, subdir))
            else:
                sub_dir_to_create_coroutines += [find_or_create(join(current_root, directory))
                                                 for directory in subdir]
        await gather(*sub_dir_to_create_coroutines)

    @staticmethod
    def get_module_init_file_content(modules):
        return "\n".join(f"from .{module} import *" for module in modules)

    @staticmethod
    def _get_single_module_init_line(tentacle):
        return f"from .{tentacle.name} import *"
