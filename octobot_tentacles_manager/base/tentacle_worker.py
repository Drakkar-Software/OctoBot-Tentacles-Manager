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
from os.path import join, isdir, sep
from octobot_commons.logging.logging_util import get_logger
from octobot_tentacles_manager.constants import TENTACLES_ARCHIVE_ROOT, PYTHON_INIT_FILE, TENTACLE_MAX_SUB_FOLDERS_LEVEL
from octobot_tentacles_manager.tentacle_data.tentacle_data_factory import TentacleDataFactory


class TentacleWorker:
    def __init__(self, reference_tentacles_dir, tentacle_path, use_confirm_prompt):
        self.logger = get_logger(self.__class__.__name__)
        self.use_confirm_prompt = use_confirm_prompt
        self.reference_tentacles_root = join(reference_tentacles_dir, TENTACLES_ARCHIVE_ROOT)
        self.tentacle_path = tentacle_path
        self.tentacle_factory = TentacleDataFactory(self.reference_tentacles_root)
        self.total_steps = 0
        self.progress = 0

    def _get_reference_tentacle_data(self):
        return [self.tentacle_factory.create_tentacle_data(tentacle_name, tentacle_type)
                for tentacle_type in self._get_tentacle_types(self.reference_tentacles_root)
                for tentacle_name in listdir(join(self.reference_tentacles_root, tentacle_type))]

    def _get_tentacle_types(self, ref_tentacles_root):
        tentacle_types = []
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
        return any(file_name.endswith(PYTHON_INIT_FILE)
                   for sub_directory in listdir(directory)
                   for file_name in listdir(join(directory, sub_directory)))
