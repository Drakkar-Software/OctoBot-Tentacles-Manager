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
from octobot_tentacles_manager.constants import TENTACLES_INSTALL_TEMP_DIR, TENTACLES_PATH
from octobot_tentacles_manager.updaters.update_worker import UpdateWorker
from octobot_tentacles_manager.util.tentacle_fetching import fetch_and_extract_tentacles, cleanup_temp_dirs

LOGGER = get_logger(__name__)
USER_HELP = """Update the given tentacle modules and install missing requirements if any. 
Does not update already filled requirements regardless of their version to avoid conflicts. 
Prefer a full tentacles update if a requirement version is creating conflicts.
    Does not edit tentacles configuration files."""


async def update_all_tentacles(tentacles_path_or_url, tentacle_path=TENTACLES_PATH, aiohttp_session=None) -> int:
    return await _update_tentacles(None, tentacles_path_or_url, tentacle_path, aiohttp_session=aiohttp_session)


async def update_tentacles(tentacle_names, tentacles_path_or_url, tentacle_path=TENTACLES_PATH,
                           aiohttp_session=None) -> int:
    return await _update_tentacles(tentacle_names, tentacles_path_or_url,
                                   tentacle_path, aiohttp_session=aiohttp_session)


async def _update_tentacles(tentacle_names, tentacles_path_or_url, tentacle_path=TENTACLES_PATH,
                            use_confirm_prompt=False, aiohttp_session=None) -> int:
    errors_count = 0
    try:
        await fetch_and_extract_tentacles(TENTACLES_INSTALL_TEMP_DIR, tentacles_path_or_url, aiohttp_session)
        update_worker = UpdateWorker(TENTACLES_INSTALL_TEMP_DIR, tentacle_path, use_confirm_prompt, aiohttp_session)
        errors_count = await update_worker.update_tentacles(tentacle_names)
    except Exception as e:
        LOGGER.exception(e, True, f"Exception when updating tentacles: {e}")
    finally:
        cleanup_temp_dirs(TENTACLES_INSTALL_TEMP_DIR)
    return errors_count
