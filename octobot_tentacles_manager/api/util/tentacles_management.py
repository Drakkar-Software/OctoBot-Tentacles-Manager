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
from octobot_commons.logging.logging_util import get_logger
from octobot_tentacles_manager.constants import TENTACLES_INSTALL_TEMP_DIR
from octobot_tentacles_manager.util.tentacle_fetching import cleanup_temp_dirs, fetch_and_extract_tentacles

LOGGER = get_logger(__name__)


async def manage_tentacles(worker, tentacle_names, tentacles_path_or_url=None, aiohttp_session=None) -> int:
    errors_count = 0
    try:
        if tentacles_path_or_url is not None:
            await fetch_and_extract_tentacles(TENTACLES_INSTALL_TEMP_DIR, tentacles_path_or_url, aiohttp_session)
        errors_count = await worker.process(tentacle_names)
    except Exception as e:
        LOGGER.exception(e, True, f"Exception during {worker.__class__.__name__} processing: {e}")
    finally:
        if tentacles_path_or_url is not None:
            cleanup_temp_dirs(TENTACLES_INSTALL_TEMP_DIR)
    return errors_count
