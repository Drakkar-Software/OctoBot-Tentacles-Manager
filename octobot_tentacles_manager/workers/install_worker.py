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
from octobot_tentacles_manager.models.tentacle import Tentacle
from octobot_tentacles_manager.util.tentacle_explorer import load_tentacle_with_metadata


class InstallWorker(TentaclesWorker):

    async def process(self, name_filter=None) -> int:
        await self.tentacles_setup_manager.create_missing_tentacles_arch()
        self.reset_worker()
        self.progress = 1
        all_tentacles = await load_tentacle_with_metadata(self.reference_tentacles_root)
        self.register_error_on_missing_tentacles(all_tentacles, name_filter)
        to_install_tentacles = [tentacle
                                for tentacle in all_tentacles
                                if self._should_tentacle_be_processed(tentacle, name_filter)]
        self.total_steps = len(to_install_tentacles)
        self.register_to_process_tentacles_modules(to_install_tentacles)
        await gather(*[self._install_tentacle(tentacle) for tentacle in to_install_tentacles])
        await self.tentacles_setup_manager.refresh_user_tentacles_setup_config_file()
        self.tentacles_setup_manager.cleanup_temp_dirs()
        self.log_summary()
        return len(self.errors)

    def _should_tentacle_be_processed(self, tentacle, name_filter):
        return name_filter is None or tentacle.name in name_filter

    async def _install_tentacle(self, tentacle):
        try:
            if tentacle.name not in self.processed_tentacles_modules:
                self.processed_tentacles_modules.append(tentacle.name)
                await self.handle_requirements(tentacle, self._try_install_from_requirements)
                tentacle_manager = TentacleManager(tentacle, self.bot_installation_path)
                await tentacle_manager.install_tentacle(self.tentacle_path)
                update_tentacle_type_init_file(tentacle, tentacle_manager.target_tentacle_path)
                self.logger.info(f"[{self.progress}/{self.total_steps}] installed {tentacle}")
        except Exception as e:
            message = f"Error when installing {tentacle.name}: {e}"
            self.errors.append(message)
            self.logger.exception(e, True, message)
        finally:
            self.progress += 1

    async def _try_install_from_requirements(self, tentacle, missing_requirements):
        for requirement, version in missing_requirements.items():
            if TentacleManager.is_requirement_satisfied(requirement, version, tentacle,
                                                        self.fetched_for_requirements_tentacles_versions):
                to_install_tentacle = Tentacle.find(self.fetched_for_requirements_tentacles, requirement)
                if to_install_tentacle is not None:
                    await self._install_tentacle(to_install_tentacle)
                else:
                    raise RuntimeError(f"Can't find {requirement} tentacle required for {tentacle.name}")
