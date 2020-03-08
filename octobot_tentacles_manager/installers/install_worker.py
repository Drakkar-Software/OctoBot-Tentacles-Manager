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
import aiofiles
from os import path, listdir
from shutil import copyfile, copytree, rmtree
from asyncio import gather

from octobot_tentacles_manager.base.tentacle_worker import TentacleWorker
from octobot_tentacles_manager.constants import TENTACLES_FOLDERS_ARCH, PYTHON_INIT_FILE, TENTACLE_MODULE_FOLDERS
from octobot_tentacles_manager.util.file_util import find_or_create
from octobot_tentacles_manager.tentacle_data.tentacle_data import TentacleData


class InstallWorker(TentacleWorker):

    async def install_all_tentacles(self):
        await self.create_missing_tentacles_arch()
        to_install_tentacles = self._get_reference_tentacle_data()
        self.total_steps = len(to_install_tentacles)
        self.progress = 1
        await gather(*[self._refresh_tentacle_dir(tentacle_data)
                       for tentacle_data in to_install_tentacles])

    async def create_missing_tentacles_arch(self):
        found_existing_installation = not await find_or_create(self.tentacle_path)
        await find_or_create(path.join(self.tentacle_path, PYTHON_INIT_FILE), False,
                             InstallWorker._get_module_init_file_content(TENTACLES_FOLDERS_ARCH.keys()))
        await InstallWorker._rec_create_missing_files(self.tentacle_path, TENTACLES_FOLDERS_ARCH)
        return found_existing_installation

    async def _refresh_tentacle_dir(self, tentacle_data):
        try:
            self._update_tentacle_folder(tentacle_data)
            await self._update_init_file(tentacle_data, path.join(self.tentacle_path, tentacle_data.tentacle_type))
            tentacle_data.load_metadata()
            self.logger.info(f"[{self.progress}/{self.total_steps}] Installed {tentacle_data}")
        except Exception as e:
            self.logger.error(f"Error when installing {tentacle_data.name}: {e}")
        finally:
            self.progress += 1

    def _update_tentacle_folder(self, tentacle_data):
        reference_tentacle_path = path.join(tentacle_data.tentacle_path, tentacle_data.name)
        target_tentacle_path = path.join(self.tentacle_path, tentacle_data.tentacle_type, tentacle_data.name)
        for tentacle_file in listdir(reference_tentacle_path):
            file_or_dir = path.join(reference_tentacle_path, tentacle_file)
            target_file_or_dir = path.join(target_tentacle_path, tentacle_file)
            if path.isfile(file_or_dir):
                copyfile(file_or_dir, target_file_or_dir)
            else:
                if tentacle_file in TENTACLE_MODULE_FOLDERS:
                    if path.exists(target_file_or_dir):
                        rmtree(target_file_or_dir)
                    copytree(file_or_dir, target_file_or_dir)

    async def _update_init_file(self, tentacle_data, target_tentacle_path):
        init_content = ""
        init_file = path.join(target_tentacle_path, PYTHON_INIT_FILE)
        init_file_exists = path.isfile(init_file)
        if init_file_exists:
            async with aiofiles.open(init_file, "r") as init_file_r:
                init_content = init_file_r.read()
        if not init_file_exists or not init_content:
            init_content = self._get_tentacle_init_header()

        if tentacle_data.name not in init_content:
            init_content = f"{init_content}\n{InstallWorker._get_init_block(tentacle_data, target_tentacle_path)}"
            async with aiofiles.open(init_file, "w+") as init_file_w:
                await init_file_w.write(init_content)

    @staticmethod
    async def _rec_create_missing_files(root_folder, files_arch):
        sub_dir_to_create_coroutines = []
        for root, subdir in files_arch.items():
            current_root = path.join(root_folder, root)
            await find_or_create(current_root)
            if isinstance(subdir, dict):
                # create python init file
                await find_or_create(path.join(current_root, PYTHON_INIT_FILE), False,
                                     InstallWorker._get_module_init_file_content(subdir))
                sub_dir_to_create_coroutines.append(InstallWorker._rec_create_missing_files(current_root, subdir))
            else:
                # create python init file
                await find_or_create(path.join(current_root, PYTHON_INIT_FILE), False,
                                     InstallWorker._get_module_init_file_content(subdir))
                sub_dir_to_create_coroutines += [find_or_create(path.join(current_root, directory))
                                                 for directory in subdir]
        await gather(*sub_dir_to_create_coroutines)

    @staticmethod
    def _get_module_init_file_content(modules):
        return "\n".join(f"from .{module} import *" for module in modules)

    @staticmethod
    def _get_tentacle_init_header():
        return """import os
from importlib import import_module

from octobot_tentacles_manager.api.inspector import check_tentacle
from octobot_commons.logging.logging_util import get_logger

LOGGER = get_logger("TentacleLoader")
PATH = os.path.dirname(os.path.realpath(__file__))

"""

    @staticmethod
    def _get_init_block(tentacle_data, tentacle_path):
        return f"""try:
    from .{tentacle_data.name} import *
    check_tentacle(import_module(".{tentacle_data.name}", "{TentacleData.to_import_path(tentacle_path)}"))
except Exception as e:
    LOGGER.exception(e, True, f'Error when loading {tentacle_data.name}: {{e}}')
"""
