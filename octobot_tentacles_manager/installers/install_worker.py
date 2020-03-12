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
from os import path
from asyncio import gather

from octobot_tentacles_manager.base_worker.tentacle_worker import import_tentacle_config_if_any, \
    is_requirement_satisfied, update_tentacle_folder, update_tentacle_type_init_file, create_tentacle_init_file
from octobot_tentacles_manager.base_worker.tentacles_worker import TentaclesWorker
from octobot_tentacles_manager.tentacle_data.tentacle_data import TentacleData
from octobot_tentacles_manager.util.tentacle_explorer import load_tentacle_with_metadata


class InstallWorker(TentaclesWorker):

    async def install_tentacles(self, name_filter=None) -> int:
        await self.create_missing_tentacles_arch()
        self.reset_worker()
        self.progress = 1
        all_tentacle_data = await load_tentacle_with_metadata(self.reference_tentacles_root)
        to_install_tentacles = [tentacle_data
                                for tentacle_data in all_tentacle_data
                                if self._should_tentacle_data_be_processed(tentacle_data, name_filter)]
        self.total_steps = len(to_install_tentacles)
        self.register_to_process_tentacles_modules(to_install_tentacles)
        await gather(*[self._install_tentacle(tentacle_data) for tentacle_data in to_install_tentacles])
        await self.refresh_tentacles_config_file()
        self.log_summary()
        return len(self.errors)

    def _should_tentacle_data_be_processed(self, tentacle_data, name_filter):
        return name_filter is None or tentacle_data.name in name_filter

    async def _install_tentacle(self, tentacle_data):
        try:
            if tentacle_data.name not in self.processed_tentacles_modules:
                self.processed_tentacles_modules.append(tentacle_data.name)
                await self.handle_requirements(tentacle_data, self._try_install_from_requirements)
                target_tentacle_path = path.join(self.tentacle_path, tentacle_data.tentacle_type)
                tentacle_module_path = path.join(target_tentacle_path, tentacle_data.name)
                update_tentacle_folder(tentacle_data, self.tentacle_path)
                await update_tentacle_type_init_file(tentacle_data, target_tentacle_path)
                await create_tentacle_init_file(tentacle_data, tentacle_module_path)
                import_tentacle_config_if_any(tentacle_module_path)
                self.logger.info(f"[{self.progress}/{self.total_steps}] installed {tentacle_data}")
        except Exception as e:
            message = f"Error when installing {tentacle_data.name}: {e}"
            self.errors.append(message)
            self.logger.exception(e, True, message)
        finally:
            self.progress += 1

    async def _try_install_from_requirements(self, tentacle_data, missing_requirements):
        for requirement, version in missing_requirements.items():
            if is_requirement_satisfied(requirement, version, tentacle_data,
                                        self.fetched_for_requirements_tentacles_versions):
                to_install_tentacle = TentacleData.find(self.fetched_for_requirements_tentacles, requirement)
                if to_install_tentacle is not None:
                    await self._install_tentacle(to_install_tentacle)
                else:
                    raise RuntimeError(f"Can't find {requirement} tentacle required for {tentacle_data.name}")
