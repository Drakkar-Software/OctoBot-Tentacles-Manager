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
from os import scandir, remove, mkdir
from os.path import exists, join
from shutil import rmtree, copytree, make_archive, copy

from octobot_commons.logging.logging_util import get_logger
from octobot_tentacles_manager.constants import TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER, TENTACLES_ARCHIVE_ROOT, \
    TENTACLES_PACKAGE_FORMAT, PYTHON_GENERATED_ELEMENTS, PYTHON_GENERATED_ELEMENTS_EXTENSION
from octobot_tentacles_manager.managers.tentacles_setup_manager import TentaclesSetupManager
from octobot_tentacles_manager.util.tentacle_explorer import load_tentacle_with_metadata


async def create_tentacles_package_from_local_tentacles(package_name, tentacles_folder, in_zip, with_dev_mode) -> int:
    logger = get_logger("tentacles_package_creator")
    try:
        # create working folder
        working_folder = join(TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER, TENTACLES_ARCHIVE_ROOT) if in_zip else package_name
        if in_zip:
            _create_zip_working_tentacles_folder(tentacles_folder, working_folder)
        else:
            _create_folder_working_tentacles_folder(tentacles_folder, working_folder)

        # remove dev-mode tentacles if necessary
        if not with_dev_mode:
            await _cleanup_in_dev_tentacles(working_folder)

        # cleanup temp working folder
        tentacles_setup_manager = TentaclesSetupManager(working_folder)
        await tentacles_setup_manager.remove_tentacle_arch_init_files()
        _remove_python_generated_files(working_folder)

        if in_zip:
            _zip_tentacles_package(package_name, TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)
            logger.info(f"Zipped tentacles package available at: {package_name}")
        else:
            logger.info(f"Cleaned tentacles folder available at: {package_name}")

        return 0
    except Exception as e:
        logger.exception(e, True, f"Error while creating tentacles archive: {e}")
        return 1


def _zip_tentacles_package(package_name, working_folder):
    # remove .zip extension if necessary
    file_name = package_name.split(f".{TENTACLES_PACKAGE_FORMAT}")[0]
    make_archive(file_name, TENTACLES_PACKAGE_FORMAT, working_folder)
    # remove working folder
    rmtree(TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)


async def _cleanup_in_dev_tentacles(tentacles_folder):
    for tentacle in load_tentacle_with_metadata(tentacles_folder):
        if tentacle.in_dev_mode:
            rmtree(join(tentacle.tentacle_path, tentacle.name))


def _create_zip_working_tentacles_folder(source_tentacles_folder, working_folder):
    if exists(TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER):
        rmtree(TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)
    mkdir(TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)
    copytree(source_tentacles_folder, working_folder)


def _create_folder_working_tentacles_folder(source_tentacles_folder, working_folder):
    if not exists(working_folder):
        copytree(source_tentacles_folder, working_folder)
    else:
        _merge_folders(source_tentacles_folder, working_folder)


def _merge_folders(to_merge_folder, dest_folder):
    dest_folder_elements = {
        element.name: element for element in scandir(dest_folder)
    }
    for element in scandir(to_merge_folder):
        dest = join(dest_folder, element.name)
        if element.is_file():
            copy(element.path, dest)
        else:
            if element.name not in dest_folder_elements:
                copytree(element.path, dest)
            else:
                _merge_folders(element.path, dest_folder_elements[element.name].path)


def _remove_python_generated_files(directory):
    for element in scandir(directory):
        element_ext = element.name.split(".")[-1]
        if element.name in PYTHON_GENERATED_ELEMENTS or \
                (element_ext in PYTHON_GENERATED_ELEMENTS_EXTENSION and element.is_file()):
            if element.is_dir():
                rmtree(element)
            elif element.is_file():
                remove(element)
        elif element.is_dir():
            _remove_python_generated_files(element)
