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
import aiofiles
from os import path
from shutil import rmtree
from asyncio import gather

from octobot_tentacles_manager.base.tentacle_worker import TentacleWorker
from octobot_tentacles_manager.constants import PYTHON_INIT_FILE
from octobot_tentacles_manager.util.tentacle_util import delete_tentacles_arch


class UninstallWorker(TentacleWorker):

    async def uninstall_tentacles(self, name_filter=None) -> int:
        self.reset_worker()
        if self.confirm_action("Remove all installed tentacles ?"
                               if name_filter is None else "Remove {', '.join(name_filter)} tentacles ?"):
            if name_filter is None:
                delete_tentacles_arch()
            else:
                self.progress = 1
                all_tentacle_data = await self.load_tentacle_with_metadata(self.tentacle_path)
                to_uninstall_tentacles = [tentacle_data
                                          for tentacle_data in all_tentacle_data
                                          if tentacle_data.name in name_filter]
                await gather(*[self._uninstall_tentacle(tentacle_data) for tentacle_data in to_uninstall_tentacles])
            await self.create_missing_tentacles_arch()
            await self.refresh_tentacle_config_file()
            self.log_summary()
        return len(self.errors)

    async def _uninstall_tentacle(self, tentacle_data):
        try:
            rmtree(path.join(tentacle_data.tentacle_path, tentacle_data.name))
            await self._update_tentacle_type_init_file(tentacle_data, tentacle_data.tentacle_path)
            self.logger.info(f"[{self.progress}/{self.total_steps}] uninstalled {tentacle_data}")
        except Exception as e:
            message = f"Error when uninstalling {tentacle_data.name}: {e}"
            self.errors.append(message)
            self.logger.exception(e, True, message)
        finally:
            self.progress += 1

    @staticmethod
    async def _update_tentacle_type_init_file(tentacle_data, target_tentacle_path):
        init_file = path.join(target_tentacle_path, PYTHON_INIT_FILE)
        if path.isfile(init_file):
            async with aiofiles.open(init_file, "r") as init_file_r:
                init_content = await init_file_r.read()
            to_remove_line = f"{TentacleWorker._get_single_module_init_line(tentacle_data)}\n"
            if to_remove_line in init_content:
                init_content = init_content.replace(to_remove_line, "")
                async with aiofiles.open(init_file, "w+") as init_file_w:
                    await init_file_w.write(init_content)
