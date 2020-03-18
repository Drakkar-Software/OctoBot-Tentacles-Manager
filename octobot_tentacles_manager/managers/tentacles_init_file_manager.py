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
import aiofiles

from octobot_tentacles_manager.constants import PYTHON_INIT_FILE
from octobot_tentacles_manager.util.file_util import find_or_create


TENTACLE_IMPORT_HEADER = """from octobot_tentacles_manager.api.inspector import check_tentacle_version
from octobot_commons.logging.logging_util import get_logger
"""


async def find_or_create_module_init_file(module_root, modules):
    await find_or_create(join(module_root, PYTHON_INIT_FILE), False, get_module_init_file_content(modules))


async def update_tentacle_type_init_file(tentacle, target_tentacle_path, remove_import=False):
    init_content = ""
    init_file = join(target_tentacle_path, PYTHON_INIT_FILE)
    if isfile(init_file):
        # load import file
        async with aiofiles.open(init_file, "r") as init_file_r:
            init_content = await init_file_r.read()
    if remove_import:
        # remove import line
        await _remove_tentacle_from_tentacle_type_init_file(init_content, tentacle, init_file)
    else:
        await _add_tentacle_to_tentacle_type_init_file(init_content, tentacle, init_file)


async def _add_tentacle_to_tentacle_type_init_file(init_content, tentacle, init_file):
    if tentacle.name not in init_content:
        # add import headers if missing
        if TENTACLE_IMPORT_HEADER not in init_content:
            init_content = f"{TENTACLE_IMPORT_HEADER}{init_content}"
        # add import line
        init_content = f"{init_content}{get_tentacle_import_block(tentacle)}"
        async with aiofiles.open(init_file, "w+") as init_file_w:
            await init_file_w.write(init_content)


async def _remove_tentacle_from_tentacle_type_init_file(init_content, tentacle, init_file):
    if init_content:
        # remove import line
        to_remove_line = f"{get_tentacle_import_block(tentacle)}\n"
        if to_remove_line in init_content:
            init_content = init_content.replace(to_remove_line, "")
            async with aiofiles.open(init_file, "w+") as init_file_w:
                await init_file_w.write(init_content)


def get_module_init_file_content(modules):
    return "\n".join(f"from .{module} import *" for module in modules)


def get_single_module_init_line(tentacle):
    return f"from .{tentacle.name} import *"


def get_tentacle_import_block(tentacle):
    return f"""
if check_tentacle_version('{tentacle.version}', '{tentacle.name}', '{tentacle.origin_package}'):
    try:
        {get_single_module_init_line(tentacle)}
    except Exception as e:
        get_logger('TentacleLoader').exception(e, True, f'Error when loading {tentacle.name}: {{e}}')
"""
