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
from os import listdir
from os.path import isdir, join, sep

from octobot_tentacles_manager.constants import PYTHON_EXT, PYTHON_INIT_FILE, TENTACLE_MAX_SUB_FOLDERS_LEVEL
from octobot_tentacles_manager.models.tentacle_factory import TentacleFactory


async def load_tentacle_with_metadata(tentacle_path):
    loaded_tentacles = _parse_all_tentacles(tentacle_path)
    await _load_all_metadata(loaded_tentacles)
    return loaded_tentacles


async def _load_all_metadata(tentacles):
    await gather(*[tentacle.initialize() for tentacle in tentacles])


def _parse_all_tentacles(root):
    factory = TentacleFactory(root)
    return [factory.create_tentacle_from_type(tentacle_name, tentacle_type)
            for tentacle_type in _get_tentacle_types(root)
            for tentacle_name in listdir(join(root, tentacle_type))
            if not tentacle_name == PYTHON_INIT_FILE]


def _get_tentacle_types(ref_tentacles_root):
    tentacle_types = []
    if isdir(ref_tentacles_root):
        _rec_get_tentacles_type(ref_tentacles_root, tentacle_types, 1, TENTACLE_MAX_SUB_FOLDERS_LEVEL)
    return tentacle_types


def _rec_get_tentacles_type(ref_tentacles_root, tentacle_types, current_level, max_level):
    if current_level <= max_level:
        for tentacle_type in listdir(ref_tentacles_root):
            tentacle_dir = join(ref_tentacles_root, tentacle_type)
            if isdir(tentacle_dir):
                full_tentacle_type = join(*tentacle_dir.split(sep)[-current_level:])
                if not _add_tentacle_type_if_is_valid(tentacle_dir, full_tentacle_type, tentacle_types):
                    _rec_get_tentacles_type(tentacle_dir, tentacle_types, current_level + 1, max_level)


def _add_tentacle_type_if_is_valid(tentacle_type_dir, tentacle_type, tentacle_types):
    if _has_tentacle_in_direct_sub_directories(tentacle_type_dir):
        tentacle_types.append(tentacle_type)
        return True
    return False


def _has_tentacle_in_direct_sub_directories(directory):
    return any((file_name.endswith(PYTHON_EXT) and not file_name == PYTHON_INIT_FILE)
               for sub_directory in listdir(directory)
               if isdir(join(directory, sub_directory))
               for file_name in listdir(join(directory, sub_directory))
               )
