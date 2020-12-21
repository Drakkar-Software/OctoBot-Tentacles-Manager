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

import os

import octobot_tentacles_manager.exporters.artifact_exporter as artifact_exporter
import octobot_tentacles_manager.models as models
import octobot_tentacles_manager.constants as constants


class TentacleExporter(artifact_exporter.ArtifactExporter):
    def __init__(self,
                 artifact: models.Tentacle,
                 tentacles_export_dir: str,
                 tentacles_folder: str,
                 should_cythonize: bool = False,
                 should_zip: bool = False,
                 with_dev_mode: bool = False):
        super().__init__(artifact,
                         tentacles_folder=tentacles_folder,
                         should_cythonize=should_cythonize,
                         should_zip=should_zip,
                         with_dev_mode=with_dev_mode)
        self.tentacles_export_dir = tentacles_export_dir
        self.tentacles_export_path: str = os.path.join(
            constants.TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER, self.artifact.name) \
            if self.should_zip else os.path.join(tentacles_export_dir, self.artifact.name)
        self.working_folder = self.tentacles_export_path

    async def prepare_export(self):
        if not os.path.exists(self.working_folder):
            os.makedirs(self.working_folder)

        if self.should_zip:
            self.copy_directory_content_to_temporary_dir(self.artifact.tentacle_module_path)
        else:
            self.copy_directory_content_to_working_dir(self.artifact.tentacle_module_path)
