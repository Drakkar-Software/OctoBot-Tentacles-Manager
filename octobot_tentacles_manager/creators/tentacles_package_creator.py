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

        tentacles_filter = util.TentacleFilter(tentacles, tentacles_white_list)
        if in_zip:
            _create_zip_working_tentacles_folder(tentacles_folder, working_folder, tentacles_filter)
        else:
            _create_folder_working_tentacles_folder(tentacles_folder, working_folder, tentacles_filter)

        # cleanup temp working folder
        tentacles_setup_manager = managers.TentaclesSetupManager(working_folder)
        await tentacles_setup_manager.remove_tentacle_arch_init_files()
        util.remove_unnecessary_files(working_folder)
        if in_zip:
            util.remove_non_tentacles_files(working_folder, logger)

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
        util.merge_folders(source_tentacles_folder, working_folder, tentacles_filter.should_ignore)
