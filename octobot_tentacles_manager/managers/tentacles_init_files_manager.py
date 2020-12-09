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
from os.path import join, isfile

from octobot_tentacles_manager.constants import PYTHON_INIT_FILE
from octobot_tentacles_manager.util.file_util import find_or_create


TENTACLE_IMPORT_HEADER = """from octobot_tentacles_manager.api.inspector import check_tentacle_version
from octobot_commons.logging.logging_util import get_logger
"""

NEW_LINE = "\n"


async def find_or_create_module_init_file(module_root, modules):
    await find_or_create(join(module_root, PYTHON_INIT_FILE), False, get_module_init_file_content(modules))


async def create_tentacle_init_file_if_necessary(tentacle_module_path, tentacle):
    init_file = join(tentacle_module_path, PYTHON_INIT_FILE)
    await find_or_create(init_file, is_directory=False, file_content=_get_default_init_file_content(tentacle))


def update_tentacle_type_init_file(tentacle, target_tentacle_path, remove_import=False):
    # Not async function to avoid conflict between read and write
    init_file = join(target_tentacle_path, PYTHON_INIT_FILE)
    if remove_import:
        # remove import line
        _remove_tentacle_from_tentacle_type_init_file(tentacle, init_file)
    else:
        _add_tentacle_to_tentacle_type_init_file(tentacle, init_file)


def _add_tentacle_to_tentacle_type_init_file(tentacle, init_file):
    init_content = ""
    if isfile(init_file):
        # load import file
        with open(init_file, "r") as init_file_r:
            init_content = init_file_r.read()
    if tentacle.name not in init_content:
        # add import headers if missing
        if TENTACLE_IMPORT_HEADER not in init_content:
            init_content = f"{TENTACLE_IMPORT_HEADER}{init_content}"
        # add import line
        init_content = f"{init_content}{get_tentacle_import_block(tentacle)}"
        with open(init_file, "w+") as init_file_w:
            init_file_w.write(init_content)


def _remove_tentacle_from_tentacle_type_init_file(tentacle, init_file):
    init_content_lines = []
    if isfile(init_file):
        # load import file
        with open(init_file, "r") as init_file_r:
            init_content_lines = init_file_r.readlines()
    if init_content_lines:
        # remove import line
        to_remove_lines_count = len(get_tentacle_import_block(tentacle).split(NEW_LINE)) - 2
        to_remove_start_index = None
        tentacle_name_identifier = f"'{tentacle.name}'"
        for index, line in enumerate(init_content_lines):
            if tentacle_name_identifier in line:
                if index > 1 and init_content_lines[index - 1] == NEW_LINE:
                    # if possible, also remove additional newline
                    to_remove_start_index = index - 1
                    to_remove_lines_count = to_remove_lines_count + 1
                else:
                    to_remove_start_index = index
                break
        if to_remove_start_index is not None:
            del init_content_lines[to_remove_start_index:to_remove_start_index + to_remove_lines_count]
            with open(init_file, "w+") as init_file_w:
                init_file_w.writelines(init_content_lines)


def get_module_init_file_content(modules):
    return NEW_LINE.join(f"from .{module} import *" for module in modules)


def _get_default_init_file_content(tentacle):
    return f"from .{tentacle.name} import {', '.join(tentacle.tentacle_class_names)}"


def _get_single_module_init_line(tentacle):
    return f"from .{tentacle.name} import *"


def get_tentacle_import_block(tentacle):
    return f"""
if check_tentacle_version('{tentacle.version}', '{tentacle.name}', '{tentacle.origin_package}'):
    try:
        {_get_single_module_init_line(tentacle)}
    except Exception as e:
        get_logger('TentacleLoader').exception(e, True, f'Error when loading {tentacle.name}: {{e}}')
"""
