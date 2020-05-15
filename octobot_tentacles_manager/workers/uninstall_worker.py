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
from asyncio import gather

from octobot_tentacles_manager.managers.tentacle_manager import TentacleManager
from octobot_tentacles_manager.managers.tentacles_init_files_manager import update_tentacle_type_init_file
from octobot_tentacles_manager.workers.tentacles_worker import TentaclesWorker
from octobot_tentacles_manager.util.tentacle_explorer import load_tentacle_with_metadata


class UninstallWorker(TentaclesWorker):

    async def process(self, name_filter=None) -> int:
        self.reset_worker()
        if self.confirm_action("Remove all installed tentacles ?"
                               if name_filter is None else "Remove {', '.join(name_filter)} tentacles ?"):
            if name_filter is None:
                self.tentacles_setup_manager.delete_tentacles_arch(force=True, with_user_config=False,
                                                                   bot_installation_path=self.bot_installation_path)
            else:
                self.progress = 1
                all_tentacles = load_tentacle_with_metadata(self.tentacle_path)
                self.register_error_on_missing_tentacles(all_tentacles, name_filter)
                to_uninstall_tentacles = [tentacle
                                          for tentacle in all_tentacles
                                          if tentacle.name in name_filter]
                await gather(*[self._uninstall_tentacle(tentacle) for tentacle in to_uninstall_tentacles])
            await self.tentacles_setup_manager.create_missing_tentacles_arch()
            await self.tentacles_setup_manager.refresh_user_tentacles_setup_config_file(
                self.tentacles_setup_config_to_update, self.tentacles_path_or_url, True)
            self.log_summary()
        return len(self.errors)

    async def _uninstall_tentacle(self, tentacle):
        try:
            tentacle_manager = TentacleManager(tentacle)
            await tentacle_manager.uninstall_tentacle()
            update_tentacle_type_init_file(tentacle, tentacle.tentacle_path, remove_import=True)
            if not self.quite_mode:
                self.logger.info(f"[{self.progress}/{self.total_steps}] uninstalled {tentacle}")
        except Exception as e:
            message = f"Error when uninstalling {tentacle.name}: {e}"
            self.errors.append(message)
            self.logger.exception(e, True, message)
        finally:
            self.progress += 1
