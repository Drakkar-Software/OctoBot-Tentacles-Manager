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
import os 
import os.path as path
import shutil 

import octobot_commons.logging as logging
import octobot_tentacles_manager.constants as constants
import octobot_tentacles_manager.creators as creators
import octobot_tentacles_manager.managers as managers
import octobot_tentacles_manager.util as util


async def create_tentacles_package_from_local_tentacles(package_name, tentacles_folder,
                                                        in_zip, with_dev_mode, cythonize) -> int:
    logger = logging.get_logger("tentacles_package_creator")
    try:
        # create working folder
        working_folder = path.join(constants.TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER,
                                   constants.TENTACLES_ARCHIVE_ROOT) if in_zip else package_name
        if in_zip:
            _create_zip_working_tentacles_folder(tentacles_folder, working_folder)
        else:
            _create_folder_working_tentacles_folder(tentacles_folder, working_folder)

        # remove dev-mode tentacles if necessary
        if not with_dev_mode:
            await _cleanup_in_dev_tentacles(working_folder)

        # cleanup temp working folder
        tentacles_setup_manager = managers.TentaclesSetupManager(working_folder)
        await tentacles_setup_manager.remove_tentacle_arch_init_files()
        _remove_unnecessary_files(working_folder)
        if in_zip:
            _remove_non_tentacles_files(working_folder, logger)

        # handle tentacles cythonization if required
        if cythonize:
            await creators.cythonize_and_compile_tentacles(working_folder)

        if in_zip:
            _zip_tentacles_package(package_name, constants.TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER, logger)
            logger.info(f"Zipped tentacles package available at: {package_name}")
        else:
            logger.info(f"Cleaned tentacles folder available at: {package_name}")

        return 0
    except Exception as e:
        logger.exception(e, True, f"Error while creating tentacles archive: {e}")
        return 1


def _zip_tentacles_package(package_name, working_folder, logger):
    # remove .zip extension if necessary
    file_name = package_name.split(f".{constants.TENTACLES_PACKAGE_FORMAT}")[0]
    shutil.make_archive(file_name, constants.TENTACLES_PACKAGE_FORMAT, working_folder)
    try:
        # remove working folder
        shutil.rmtree(constants.TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)
    except Exception as e:
        logger.error(f"Error when cleaning up temporary folder: {e}")


async def _cleanup_in_dev_tentacles(tentacles_folder):
    for tentacle in util.load_tentacle_with_metadata(tentacles_folder):
        if tentacle.in_dev_mode:
            shutil.rmtree(path.join(tentacle.tentacle_path, tentacle.name))


def _create_zip_working_tentacles_folder(source_tentacles_folder, working_folder):
    if path.exists(constants.TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER):
        shutil.rmtree(constants.TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)
    os.mkdir(constants.TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)
    shutil.copytree(source_tentacles_folder, working_folder, ignore=_should_ignore)


def _create_folder_working_tentacles_folder(source_tentacles_folder, working_folder):
    if not path.exists(working_folder):
        shutil.copytree(source_tentacles_folder, working_folder, ignore=_should_ignore)
    else:
        _merge_folders(source_tentacles_folder, working_folder)


def _should_ignore(_, names):
    return [name
            for name in names
            if name in constants.TENTACLES_PACKAGE_IGNORED_ELEMENTS]


def _merge_folders(to_merge_folder, dest_folder):
    dest_folder_elements = {
        element.name: element for element in os.scandir(dest_folder)
    }
    for element in os.scandir(to_merge_folder):
        dest = path.join(dest_folder, element.name)
        if element.is_file():
            shutil.copy(element.path, dest)
        else:
            if element.name not in dest_folder_elements:
                shutil.copytree(element.path, dest)
            else:
                _merge_folders(element.path, dest_folder_elements[element.name].path)


def _remove_unnecessary_files(directory):
    for element in os.scandir(directory):
        element_ext = element.name.split(".")[-1]
        if element.name in constants.PYTHON_GENERATED_ELEMENTS or \
                (element_ext in constants.PYTHON_GENERATED_ELEMENTS_EXTENSION and element.is_file()):
            if element.is_dir():
                shutil.rmtree(element)
            elif element.is_file():
                os.remove(element)
        elif element.is_dir():
            _remove_unnecessary_files(element)


def _remove_non_tentacles_files(directory, logger):
    for element in os.scandir(directory):
        if element.name not in set(constants.TENTACLES_FOLDERS_ARCH):
            try:
                if element.is_dir():
                    shutil.rmtree(element)
                elif element.is_file():
                    os.remove(element)
            except Exception as e:
                logger.error(f"Error when cleaning up temporary folder: {e}")
