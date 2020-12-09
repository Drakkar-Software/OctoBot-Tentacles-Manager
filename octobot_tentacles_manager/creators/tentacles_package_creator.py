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


async def create_tentacles_package_from_local_tentacles(package_name, tentacles_folder, exported_tentacles_package,
                                                        in_zip, with_dev_mode, cythonize) -> int:
    logger = logging.get_logger("tentacles_package_creator")
    try:
        # create working folder
        working_folder = path.join(constants.TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER,
                                   constants.TENTACLES_ARCHIVE_ROOT) if in_zip else package_name

        tentacles_white_list = None
        tentacles = []
        if not with_dev_mode or exported_tentacles_package is not None:
            tentacles = util.load_tentacle_with_metadata(tentacles_folder)
            # remove dev-mode tentacles if necessary
            tentacles_white_list = tentacles if with_dev_mode else _filter_in_dev_tentacles(tentacles)
            if exported_tentacles_package is not None:
                # only keep tentacles from the tentacles package to export
                tentacles_white_list = util.get_tentacles_from_package(tentacles_white_list, exported_tentacles_package)

        tentacles_filter = TentacleFilter(tentacles, tentacles_white_list)
        if in_zip:
            _create_zip_working_tentacles_folder(tentacles_folder, working_folder, tentacles_filter)
        else:
            _create_folder_working_tentacles_folder(tentacles_folder, working_folder, tentacles_filter)

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


def _filter_in_dev_tentacles(tentacles):
    return [
        tentacle
        for tentacle in tentacles
        if not tentacle.in_dev_mode
    ]


def _create_zip_working_tentacles_folder(source_tentacles_folder, working_folder, tentacles_filter):
    if path.exists(constants.TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER):
        shutil.rmtree(constants.TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)
    os.mkdir(constants.TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER)
    shutil.copytree(source_tentacles_folder, working_folder, ignore=tentacles_filter.should_ignore)


def _create_folder_working_tentacles_folder(source_tentacles_folder, working_folder, tentacles_filter):
    if not path.exists(working_folder):
        shutil.copytree(source_tentacles_folder, working_folder, ignore=tentacles_filter.should_ignore)
    else:
        _merge_folders(source_tentacles_folder, working_folder, tentacles_filter.should_ignore)


class TentacleFilter:
    def __init__(self, full_tentacles_list, tentacles_white_list):
        self.tentacles_white_list = tentacles_white_list
        self.full_tentacles_list = full_tentacles_list
        self.tentacle_paths_black_list = [] if self.tentacles_white_list is None else [
            path.join(tentacle.tentacle_path, tentacle.name)
            for tentacle in self.full_tentacles_list
            if tentacle not in self.tentacles_white_list
        ]
        self.ignored_elements = constants.TENTACLES_PACKAGE_IGNORED_ELEMENTS

    def should_ignore(self, folder_path, names):
        return [name
                for name in names
                if self._should_ignore(folder_path, name)]

    def _should_ignore(self, element_path, element_name):
        if element_name in self.ignored_elements:
            return True
        if self.tentacles_white_list is not None:
            candidate_path = path.join(element_path, element_name)
            return path.isdir(candidate_path) and candidate_path in self.tentacle_paths_black_list
        return False


def _merge_folders(to_merge_folder, dest_folder, ignore_func):
    dest_folder_elements = {
        element.name: element for element in os.scandir(dest_folder)
    }
    elements = list(os.scandir(to_merge_folder))
    ignored_elements = ignore_func(to_merge_folder, (e.name for e in elements))
    filtered_elements = [element
                         for element in elements
                         if element.name not in ignored_elements]
    for element in filtered_elements:
        dest = path.join(dest_folder, element.name)
        if element.is_file():
            shutil.copy(element.path, dest)
        else:
            if element.name not in dest_folder_elements:
                shutil.copytree(element.path, dest, ignore=ignore_func)
            else:
                _merge_folders(element.path, dest_folder_elements[element.name].path, ignore_func)


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
