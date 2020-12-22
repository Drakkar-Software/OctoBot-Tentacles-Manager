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

import octobot_tentacles_manager.constants as constants


class Artifact:
    ARTIFACT_NAME = "artifact"

    def __init__(self, name):
        self.name: str = name
        self.version: str = constants.UNKNOWN_ARTIFACT_VERSION
        self.origin_package: str = constants.UNKNOWN_TENTACLES_PACKAGE_LOCATION
        self.origin_repository: str = constants.UNKNOWN_REPOSITORY_LOCATION
        self.output_path: str = None

    def is_valid(self):
        return self.version is not None

    def __str__(self):
        str_rep = f"{self.name} {Artifact.ARTIFACT_NAME} ["
        if self.is_valid():
            return f"version: {self.version}]"
        else:
            return f"{str_rep}]"
