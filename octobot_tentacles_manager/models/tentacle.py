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
import json
from os.path import join

import aiofiles

from octobot_tentacles_manager.constants import TENTACLE_METADATA, METADATA_VERSION, METADATA_ORIGIN_PACKAGE, \
    METADATA_TENTACLES, METADATA_TENTACLES_REQUIREMENTS, TENTACLE_REQUIREMENT_VERSION_EQUALS, METADATA_DEV_MODE


class Tentacle:
    def __init__(self, tentacle_root_path, name, tentacle_type):
        self.tentacle_root_path = tentacle_root_path
        self.name = name
        self.tentacle_type = tentacle_type
        self.tentacle_path = join(self.tentacle_root_path, self.tentacle_type.to_path())
        self.version = None
        self.tentacle_class_names = None
        self.origin_package = None
        self.tentacles_requirements = None
        self.in_dev_mode = False
        self.metadata = {}

    async def initialize(self):
        async with aiofiles.open(join(self.tentacle_path, self.name, TENTACLE_METADATA), "r") as metadata_file:
            self.metadata = json.loads(await metadata_file.read())
            self.version = self.metadata[METADATA_VERSION]
            self.origin_package = self.metadata[METADATA_ORIGIN_PACKAGE]
            self.tentacle_class_names = self.metadata[METADATA_TENTACLES]
            self.tentacles_requirements = self.metadata[METADATA_TENTACLES_REQUIREMENTS]
            if METADATA_DEV_MODE in self.metadata:
                self.in_dev_mode = self.metadata[METADATA_DEV_MODE]

    @staticmethod
    def find(iterable, name):
        for tentacle in iterable:
            if tentacle.name == name:
                return tentacle
        return None

    def is_valid(self):
        return self.version is not None

    def get_simple_tentacle_type(self):
        return self.tentacle_type.get_last_element()

    def __str__(self):
        str_rep = f"{self.name} tentacle [type: {self.tentacle_type}"
        if self.is_valid():
            return f"{str_rep}, version: {self.version}]"
        else:
            return f"{str_rep}]"

    def extract_tentacle_requirements(self):
        return [self._parse_requirements(component) for component in self.tentacles_requirements]

    @staticmethod
    def _parse_requirements(requirement):
        if TENTACLE_REQUIREMENT_VERSION_EQUALS in requirement:
            return requirement.split(TENTACLE_REQUIREMENT_VERSION_EQUALS)
        else:
            return [requirement, None]
