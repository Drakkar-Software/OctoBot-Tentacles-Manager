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
from octobot_tentacles_manager.util.tentacle_util import tentacles_arch_exists as util_tentacles_arch_exists


def tentacles_arch_exists():
    return util_tentacles_arch_exists()


def check_tentacle(module, verbose=True):
    logger = get_logger("TentacleChecker")
    try:
        if module.ORIGIN_PACKAGE == DEFAULT_TENTACLES_PACKAGE:
            if LooseVersion(module.VERSION) < LooseVersion(TENTACLE_CURRENT_MINIMUM_DEFAULT_TENTACLES_VERSION) \
                    and verbose:
                logger.error(f"Incompatible tentacle {module.NAME}: version {module.VERSION}, "
                             f"minimum expected: {TENTACLE_CURRENT_MINIMUM_DEFAULT_TENTACLES_VERSION} this tentacle "
                             f"may not work properly. Please update your tentacles ('start.py -p update {module.NAME}' "
                             f"or 'start.py -p update all')")
    except Exception as e:
        if verbose:
            logger.error(f"Error when reading tentacle metadata: {e}")
