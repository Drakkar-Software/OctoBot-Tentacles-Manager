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
from octobot_tentacles_manager.constants import TENTACLES_PATH, DEFAULT_BOT_PATH
from octobot_tentacles_manager.api.util.tentacles_management import manage_tentacles
from octobot_tentacles_manager.workers.uninstall_worker import UninstallWorker


USER_HELP = """Uninstall the given tentacle modules. 
    Does not delete the associated tentacle configuration."""


async def uninstall_all_tentacles(tentacle_path=TENTACLES_PATH,
                                  bot_path=DEFAULT_BOT_PATH, use_confirm_prompt=False) -> int:
    return await _uninstall_tentacles(None, tentacle_path, bot_path, use_confirm_prompt)


async def uninstall_tentacles(tentacle_names,
                              tentacle_path=TENTACLES_PATH,
                              bot_path=DEFAULT_BOT_PATH,
                              use_confirm_prompt=False) -> int:
    return await _uninstall_tentacles(tentacle_names, tentacle_path, bot_path, use_confirm_prompt)


async def _uninstall_tentacles(tentacle_names,
                               tentacle_path=TENTACLES_PATH,
                               bot_path=DEFAULT_BOT_PATH,
                               use_confirm_prompt=False) -> int:
    uninstall_worker = UninstallWorker(None, tentacle_path, bot_path, use_confirm_prompt, None)
    return await manage_tentacles(uninstall_worker, tentacle_names)
