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
from distutils.version import LooseVersion

from octobot_commons.logging.logging_util import get_logger
from octobot_tentacles_manager.constants import DEFAULT_TENTACLES_PACKAGE, \
    TENTACLE_CURRENT_MINIMUM_DEFAULT_TENTACLES_VERSION
from octobot_tentacles_manager.loaders.tentacle_loading import get_tentacle, get_resources_path, \
    get_documentation_file_path, get_tentacle_classes


def get_installed_tentacles_modules() -> set:
    return set(tentacle for tentacle in get_tentacle_classes().values())


def get_tentacle_group(klass) -> str:
    return get_tentacle(klass).tentacle_group


def get_tentacle_version(klass) -> str:
    return get_tentacle(klass).version


def get_tentacle_origin_package(klass) -> str:
    return get_tentacle(klass).origin_package


def get_tentacle_module_name(klass) -> str:
    return get_tentacle(klass).name


def get_tentacle_resources_path(klass) -> str:
    return get_resources_path(klass)


def get_tentacle_documentation_path(klass) -> str:
    return get_documentation_file_path(klass)


def check_tentacle_version(version, name, origin_package, verbose=True) -> bool:
    logger = get_logger("TentacleChecker")
    try:
        if origin_package == DEFAULT_TENTACLES_PACKAGE:
            if LooseVersion(version) < LooseVersion(TENTACLE_CURRENT_MINIMUM_DEFAULT_TENTACLES_VERSION) \
                    and verbose:
                logger.error(f"Incompatible tentacle {name}: version {version}, "
                             f"minimum expected: {TENTACLE_CURRENT_MINIMUM_DEFAULT_TENTACLES_VERSION} this tentacle "
                             f"may not work properly. Please update your tentacles ('start.py -p update {name}' "
                             f"or 'start.py -p update all')")
                return False
    except Exception as e:
        if verbose:
            logger.error(f"Error when reading tentacle metadata: {e}")
    return True
