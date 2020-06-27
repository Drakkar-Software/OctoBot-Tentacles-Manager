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
from os.path import join

from octobot_tentacles_manager.managers.tentacle_manager import TentacleManager
from octobot_tentacles_manager.managers.tentacles_init_files_manager import update_tentacle_type_init_file, \
    create_tentacle_init_file_if_necessary
from octobot_tentacles_manager.workers.tentacles_worker import TentaclesWorker
from octobot_tentacles_manager.util.tentacle_explorer import load_tentacle_with_metadata


class RepairWorker(TentaclesWorker):

    def __init__(self,
                 reference_tentacles_dir,
                 tentacle_path,
                 bot_installation_path,
                 use_confirm_prompt,
                 aiohttp_session,
                 bot_install_dir):
        super().__init__(reference_tentacles_dir,
                         tentacle_path,
                         bot_installation_path,
                         use_confirm_prompt,
                         aiohttp_session,
                         bot_install_dir=bot_install_dir)
        self.verbose = True

    async def process(self, name_filter=None) -> int:
        # force reset of all init files
        await self.tentacles_setup_manager.remove_tentacle_arch_init_files()
        # create missing files and folders
        await self.tentacles_setup_manager.create_missing_tentacles_arch()
        self.reset_worker()
        self.progress = 1
        existing_tentacles = load_tentacle_with_metadata(self.tentacle_path)
        self.total_steps = len(existing_tentacles)
        await gather(*[self._repair_tentacle(tentacle) for tentacle in existing_tentacles])
        await self.tentacles_setup_manager.refresh_user_tentacles_setup_config_file(
            force_update_registered_tentacles=True
        )
        self.log_summary()
        return len(self.errors)

    async def _repair_tentacle(self, tentacle):
        try:
            tentacle_module_path = join(tentacle.tentacle_path, tentacle.name)
            tentacle_manager = TentacleManager(tentacle, self.bot_installation_path)
            await create_tentacle_init_file_if_necessary(tentacle_module_path, tentacle)
            tentacle_manager.import_tentacle_config_if_any(tentacle_module_path)
            update_tentacle_type_init_file(tentacle, tentacle.tentacle_path)
            if self.verbose:
                self.logger.info(f"[{self.progress}/{self.total_steps}] {tentacle} ready to use")
        except Exception as e:
            message = f"Error when repairing {tentacle.name}: {e}"
            self.errors.append(message)
            self.logger.exception(e, True, message)
        finally:
            self.progress += 1
