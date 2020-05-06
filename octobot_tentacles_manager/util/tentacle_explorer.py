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
from os import scandir, DirEntry
from os.path import isdir, join, sep

from octobot_tentacles_manager.constants import PYTHON_EXT, PYTHON_INIT_FILE, TENTACLE_MAX_SUB_FOLDERS_LEVEL, \
    FOLDERS_BLACK_LIST
from octobot_tentacles_manager.models.tentacle_factory import TentacleFactory
from octobot_tentacles_manager.models.tentacle_type import TentacleType


def load_tentacle_with_metadata(tentacle_path: str):
    loaded_tentacles = _parse_all_tentacles(tentacle_path)
    _load_all_metadata(loaded_tentacles)
    return loaded_tentacles


def _load_all_metadata(tentacles):
    for tentacle in tentacles:
        tentacle.sync_initialize()


def _parse_all_tentacles(root: str):
    factory = TentacleFactory(root)
    return [factory.create_tentacle_from_type(tentacle_entry.name, tentacle_type)
            for tentacle_type in _get_tentacle_types(root)
            for tentacle_entry in scandir(join(root, tentacle_type.to_path()))
            if not (tentacle_entry.name == PYTHON_INIT_FILE or tentacle_entry.name in FOLDERS_BLACK_LIST)]


def _get_tentacle_types(ref_tentacles_root):
    tentacle_types = []
    if isdir(ref_tentacles_root):
        _find_tentacles_type_in_directories(ref_tentacles_root, tentacle_types)
    return tentacle_types


def _find_tentacles_type_in_directories(ref_tentacles_root: DirEntry, tentacle_types: list, current_level=1):
    if current_level <= TENTACLE_MAX_SUB_FOLDERS_LEVEL:
        for tentacle_type_entry in scandir(ref_tentacles_root):
            if tentacle_type_entry.is_dir():
                _explore_tentacle_dir(tentacle_type_entry, tentacle_types, current_level)


def _explore_tentacle_dir(tentacle_type_entry: DirEntry, tentacle_types: list, nesting_level: int):
    # full_tentacle_type_path is the path to the current directory starting from the most global Tentacle type without
    # anything before it:
    # ex: with a at tentacle_dir="downloaded_tentacles/xyz/Backtesting/importers" then
    # full_tentacle_type_path will be "Backtesting/importers"
    full_tentacle_type_path = tentacle_type_entry.path.split(sep)[-nesting_level:]
    if not _add_tentacle_type_if_is_valid(tentacle_type_entry, join(*full_tentacle_type_path), tentacle_types):
        # no tentacle in this folder, look into nested folders
        _find_tentacles_type_in_directories(tentacle_type_entry, tentacle_types, nesting_level + 1)


def _add_tentacle_type_if_is_valid(tentacle_type_entry: DirEntry, full_tentacle_type_path: str, tentacle_types: list):
    if _has_tentacle_in_direct_sub_directories(tentacle_type_entry):
        tentacle_types.append(TentacleType(full_tentacle_type_path))
        return True
    return False


def _has_tentacle_in_direct_sub_directories(directory_entry: DirEntry):
    return any((file_entry.name.endswith(PYTHON_EXT) and not file_entry.name == PYTHON_INIT_FILE)
               for sub_directory_entry in scandir(directory_entry)
               if sub_directory_entry.is_dir()
               for file_entry in scandir(sub_directory_entry)
               )
