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
from os import listdir, path
from os.path import join, isdir, sep
from shutil import copyfile
from asyncio import gather, Event, wait_for

from octobot_commons.logging.logging_util import get_logger
from octobot_tentacles_manager.configuration.global_tentacle_configuration import GlobalTentacleConfiguration
from octobot_tentacles_manager.constants import TENTACLES_ARCHIVE_ROOT, \
    TENTACLE_MAX_SUB_FOLDERS_LEVEL, TENTACLE_CONFIG, CONFIG_SCHEMA_EXT, USER_TENTACLE_SPECIFIC_CONFIG_PATH, CONFIG_EXT, \
    TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR, DEFAULT_TENTACLES_URL, PYTHON_EXT, DEFAULT_TENTACLE_CONFIG, \
    PYTHON_INIT_FILE
from octobot_tentacles_manager.tentacle_data.tentacle_data_factory import TentacleDataFactory
from octobot_tentacles_manager.util.tentacle_fetching import fetch_and_extract_tentacles


class TentacleWorker:
    TENTACLES_FETCHING_TIMEOUT = 120

    def __init__(self, reference_tentacles_dir, tentacle_path, use_confirm_prompt, aiohttp_session):
        self.logger = get_logger(self.__class__.__name__)
        self.aiohttp_session = aiohttp_session
        self.use_confirm_prompt = use_confirm_prompt
        self.default_tentacle_config = DEFAULT_TENTACLE_CONFIG

        self.reference_tentacles_root = join(reference_tentacles_dir, TENTACLES_ARCHIVE_ROOT)
        self.tentacle_path = tentacle_path

        self.total_steps = 0
        self.progress = 0
        self.errors = []

        self.to_process_tentacle_modules = {}
        self.processed_tentacles_modules = []

        self.fetched_for_requirements_tentacles = []
        self.fetched_for_requirements_tentacles_versions = {}
        self.fetching_requirements = False
        self.requirements_downloading_event = Event()

    def reset_worker(self):
        self.errors = []

        self.to_process_tentacle_modules = {}
        self.processed_tentacles_modules = []

        self.fetched_for_requirements_tentacles = []
        self.fetched_for_requirements_tentacles_versions = {}
        self.fetching_requirements = False
        self.requirements_downloading_event = Event()

    @staticmethod
    def import_tentacle_config_if_any(target_tentacle_path, replace=False):
        target_tentacle_config_path = path.join(target_tentacle_path, TENTACLE_CONFIG)
        for config_file in listdir(target_tentacle_config_path):
            if config_file.endswith(CONFIG_EXT) and not config_file.endswith(CONFIG_SCHEMA_EXT):
                target_user_path = path.join(USER_TENTACLE_SPECIFIC_CONFIG_PATH, config_file)
                if replace or not path.exists(target_user_path):
                    copyfile(path.join(target_tentacle_config_path, config_file), target_user_path)

    async def refresh_tentacle_config_file(self):
        available_tentacle_data = await self.load_tentacle_with_metadata(self.tentacle_path)
        tentacle_global_config = GlobalTentacleConfiguration()
        await tentacle_global_config.read_config()
        await tentacle_global_config.fill_tentacle_config(available_tentacle_data, self.default_tentacle_config)
        await tentacle_global_config.save_config()

    def log_summary(self):
        if self.errors:
            self.logger.info(" *** Error summary: ***")
            for error in self.errors:
                self.logger.error(f"Error when handling tentacle: {error}")
        else:
            self.logger.info(" *** All tentacles have been successfully processed ***")

    def register_to_process_tentacles_modules(self, to_process_tentacle_data):
        self.to_process_tentacle_modules = self._get_version_by_tentacle_data(to_process_tentacle_data)

    async def handle_requirements(self, tentacle_data, callback):
        missing_requirements = self._find_tentacles_missing_requirements(tentacle_data,
                                                                         self.to_process_tentacle_modules)
        if missing_requirements:
            if not self.fetching_requirements:
                self.fetching_requirements = True
                await self._fetch_all_available_tentacles()
            else:
                await wait_for(self.requirements_downloading_event.wait(), self.TENTACLES_FETCHING_TIMEOUT)
            await callback(tentacle_data, missing_requirements)

    async def load_tentacle_with_metadata(self, tentacle_path):
        loaded_tentacle_data = self._parse_all_tentacle_data(tentacle_path)
        await self.load_all_metadata(loaded_tentacle_data)
        return loaded_tentacle_data

    def _parse_all_tentacle_data(self, root):
        factory = TentacleDataFactory(root)
        return [factory.create_tentacle_data_from_type(tentacle_name, tentacle_type)
                for tentacle_type in self._get_tentacle_types(root)
                for tentacle_name in listdir(join(root, tentacle_type))
                if not tentacle_name == PYTHON_INIT_FILE]

    async def _fetch_all_available_tentacles(self):
        # try getting it from available tentacles
        await gather(*[self._fetch_tentacles_for_requirement(repo)
                       for repo in self._get_available_tentacles_repos()])
        self.requirements_downloading_event.set()

    async def _fetch_tentacles_for_requirement(self, repo):
        await fetch_and_extract_tentacles(repo, DEFAULT_TENTACLES_URL, self.aiohttp_session, merge_dirs=True)
        requirements_tentacles_path = path.join(TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR, TENTACLES_ARCHIVE_ROOT)
        self.fetched_for_requirements_tentacles = await self.load_tentacle_with_metadata(requirements_tentacles_path)
        self.fetched_for_requirements_tentacles_versions = \
            self._get_version_by_tentacle_data(self.fetched_for_requirements_tentacles)

    def _get_available_tentacles_repos(self):
        # TODO: add advanced tentacles repos
        return [TENTACLES_REQUIREMENTS_INSTALL_TEMP_DIR]

    @staticmethod
    def _get_version_by_tentacle_data(all_tentacle_data):
        return {tentacle_data.name: tentacle_data.version
                for tentacle_data in all_tentacle_data}

    @staticmethod
    async def load_all_metadata(tentacle_data_list):
        await gather(*[tentacle_data.load_metadata() for tentacle_data in tentacle_data_list])

    def _find_tentacles_missing_requirements(self, tentacle_data, version_by_modules):
        missing_requirements = {}
        if tentacle_data.tentacles_requirements:
            # check if requirement is in tentacles to be installed in this call
            for requirement, version in tentacle_data.extract_tentacle_requirements():
                if not self._is_requirement_satisfied(requirement, version, tentacle_data, version_by_modules):
                    missing_requirements[requirement] = version
        return missing_requirements

    def _is_requirement_satisfied(self, requirement, version, tentacle_data, version_by_modules):
        satisfied = False
        if requirement in version_by_modules:
            available = version_by_modules[requirement]
            if version is None:
                satisfied = True
            elif version != available:
                self.logger.error(f"Incompatible tentacle version requirement for "
                                  f"{tentacle_data.name}: requires {version}, installed: "
                                  f"{available}. This tentacle might not work as expected")
                satisfied = True
        return satisfied

    def _get_tentacle_types(self, ref_tentacles_root):
        tentacle_types = []
        if isdir(ref_tentacles_root):
            self._rec_get_tentacles_type(ref_tentacles_root, tentacle_types, 1, TENTACLE_MAX_SUB_FOLDERS_LEVEL)
        return tentacle_types

    def _rec_get_tentacles_type(self, ref_tentacles_root, tentacle_types, current_level, max_level):
        if current_level <= max_level:
            for tentacle_type in listdir(ref_tentacles_root):
                tentacle_dir = join(ref_tentacles_root, tentacle_type)
                if isdir(tentacle_dir):
                    full_tentacle_type = join(*tentacle_dir.split(sep)[-current_level:])
                    if not self._add_tentacle_type_if_is_valid(tentacle_dir, full_tentacle_type, tentacle_types):
                        self._rec_get_tentacles_type(tentacle_dir, tentacle_types, current_level+1, max_level)

    def _add_tentacle_type_if_is_valid(self, tentacle_type_dir, tentacle_type, tentacle_types):
        if self._has_tentacle_in_direct_sub_directories(tentacle_type_dir):
            tentacle_types.append(tentacle_type)
            return True
        return False

    @staticmethod
    def _has_tentacle_in_direct_sub_directories(directory):
        return any((file_name.endswith(PYTHON_EXT) and not file_name == PYTHON_INIT_FILE)
                   for sub_directory in listdir(directory)
                   if isdir(join(directory, sub_directory))
                   for file_name in listdir(join(directory, sub_directory))
                   )
