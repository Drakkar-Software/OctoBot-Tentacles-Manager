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
from shutil import copyfile, rmtree, copytree

import aiofiles

from octobot_commons.logging.logging_util import get_logger
from octobot_tentacles_manager.constants import TENTACLE_CONFIG, CONFIG_SCHEMA_EXT, CONFIG_EXT, \
    USER_TENTACLE_SPECIFIC_CONFIG_PATH, TENTACLE_MODULE_FOLDERS, PYTHON_INIT_FILE

LOGGER = get_logger("TentacleWorker")


def import_tentacle_config_if_any(target_tentacle_path, replace=False):
    target_tentacle_config_path = path.join(target_tentacle_path, TENTACLE_CONFIG)
    for config_file in listdir(target_tentacle_config_path):
        if config_file.endswith(CONFIG_EXT) and not config_file.endswith(CONFIG_SCHEMA_EXT):
            target_user_path = path.join(USER_TENTACLE_SPECIFIC_CONFIG_PATH, config_file)
            if replace or not path.exists(target_user_path):
                copyfile(path.join(target_tentacle_config_path, config_file), target_user_path)


def find_tentacles_missing_requirements(tentacle_data, version_by_modules):
    # check if requirement is in tentacles to be installed in this call
    return {
        requirement: version
        for requirement, version in tentacle_data.extract_tentacle_requirements()
        if not is_requirement_satisfied(requirement, version, tentacle_data, version_by_modules)
    }


def is_requirement_satisfied(requirement, version, tentacle_data, version_by_modules):
    satisfied = False
    if requirement in version_by_modules:
        available = version_by_modules[requirement]
        if version is None:
            satisfied = True
        elif version != available:
            LOGGER.error(f"Incompatible tentacle version requirement for "
                         f"{tentacle_data.name}: requires {version}, installed: "
                         f"{available}. This tentacle might not work as expected")
            satisfied = True
    return satisfied


def update_tentacle_folder(tentacle_data, tentacle_path):
    reference_tentacle_path = path.join(tentacle_data.tentacle_path, tentacle_data.name)
    target_tentacle_path = path.join(tentacle_path, tentacle_data.tentacle_type, tentacle_data.name)
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


async def update_tentacle_type_init_file(tentacle_data, target_tentacle_path):
    init_content = ""
    init_file = path.join(target_tentacle_path, PYTHON_INIT_FILE)
    if path.isfile(init_file):
        async with aiofiles.open(init_file, "r") as init_file_r:
            init_content = await init_file_r.read()
    if tentacle_data.name not in init_content:
        init_content = f"{init_content}{get_single_module_init_line(tentacle_data)}\n"
        async with aiofiles.open(init_file, "w+") as init_file_w:
            await init_file_w.write(init_content)


async def create_tentacle_init_file(tentacle_data, tentacle_module_path):
    init_file = path.join(tentacle_module_path, PYTHON_INIT_FILE)
    init_content = _get_init_block(tentacle_data)
    async with aiofiles.open(init_file, "w+") as init_file_w:
        await init_file_w.write(init_content)


def get_module_init_file_content(modules):
    return "\n".join(f"from .{module} import *" for module in modules)


def get_single_module_init_line(tentacle_data):
    return f"from .{tentacle_data.name} import *"


def _get_init_block(tentacle_data):
    return f"""from octobot_tentacles_manager.api.inspector import check_tentacle_version
from octobot_commons.logging.logging_util import get_logger

if check_tentacle_version('{tentacle_data.version}', '{tentacle_data.name}', '{tentacle_data.origin_package}'):
    try:
        {get_single_module_init_line(tentacle_data)}
    except Exception as e:
        get_logger('TentacleLoader').exception(e, True, f'Error when loading {tentacle_data.name}: {{e}}')
"""
