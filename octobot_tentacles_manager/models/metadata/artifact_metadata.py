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

import octobot_tentacles_manager.enums as enums
import octobot_tentacles_manager.models.artifact as artifact_model


class ArtifactMetadata:
    METADATA_FILE = "metadata.yaml"
    METADATA_VERSION = "version"
    METADATA_NAME = "name"
    METADATA_ARTIFACT_TYPE = "type"
    METADATA_REPOSITORY = "repository"

    def __init__(self, artifact: artifact_model.Artifact):
        self.artifact: artifact_model.Artifact = artifact
        self.version: str = self.artifact.version
        self.artifact_type: enums.ArtifactTypes = None

    def to_dict(self) -> dict:
        return {
            self.METADATA_NAME: self.artifact.name,
            self.METADATA_VERSION: self.artifact.version,
            self.METADATA_ARTIFACT_TYPE: self.artifact_type.value,
            self.METADATA_REPOSITORY: self.artifact.origin_repository,
        }
