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
import shutil
import yaml

import octobot_tentacles_manager.exporters.artifact_exporter as artifact_exporter
import octobot_tentacles_manager.models as models
import octobot_tentacles_manager.util as util
import octobot_tentacles_manager.constants as constants


class TentacleBundleExporter(artifact_exporter.ArtifactExporter):
    def __init__(self,
                 artifact: models.TentacleBundle,
                 tentacles_folder: str,
                 bundle_output_dir: str,
                 should_zip: bool = False,
                 should_remove_artifacts_after_use: bool = False):
        super().__init__(artifact,
                         tentacles_folder=tentacles_folder,
                         should_cythonize=False,
                         should_zip=should_zip,
                         with_dev_mode=False)
        self.should_remove_artifacts_after_use = should_remove_artifacts_after_use
        self.bundle_output_dir: str = os.path.join(
            constants.TENTACLES_PACKAGE_CREATOR_TEMP_FOLDER, self.artifact.name) \
            if self.should_zip else os.path.join(bundle_output_dir, self.artifact.name)
        self.working_folder = self.bundle_output_dir

    async def prepare_export(self):
        if not os.path.exists(self.working_folder):
            os.makedirs(self.working_folder)

        for artifact in self.artifact.artifacts:
            # copy artifact content
            if os.path.isfile(artifact.output_path):
                shutil.copyfile(artifact.output_path, os.path.join(self.working_folder,
                                                                   os.path.basename(artifact.output_path)))
            else:
                if self.should_zip:
                    self.copy_directory_content_to_temporary_dir(artifact.output_path)
                else:
                    self.copy_directory_content_to_working_dir(artifact.output_path)

            # add artifact metadata
            artifact_metadata = models.MetadataFactory(artifact).create_metadata_instance()
            with open(os.path.join(self.working_folder, artifact_metadata.METADATA_FILE), "w") as metadata_file:
                metadata_file.write(yaml.dump(artifact_metadata.to_dict()))

    async def after_export(self) -> None:
        """
        Remove artifacts origin file or folder after bundling if necessary
        :return: None
        """
        if self.should_remove_artifacts_after_use:
            for artifact in self.artifact.artifacts:
                util.remove_dir_or_file_from_path(artifact.output_path)