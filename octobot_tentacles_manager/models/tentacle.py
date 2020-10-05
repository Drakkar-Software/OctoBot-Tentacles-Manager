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
import os.path as path

import aiofiles

import octobot_tentacles_manager.constants as constants


class Tentacle:
    def __init__(self, tentacle_root_path, name, tentacle_type):
        self.tentacle_root_path = tentacle_root_path
        self.name = name
        self.tentacle_type = tentacle_type
        self.tentacle_root_type = self.tentacle_type.get_root_type()
        self.tentacle_path = path.join(self.tentacle_root_path, self.tentacle_type.to_path())
        self.version = None
        self.tentacle_class_names = []
        self.origin_package = constants.UNKNOWN_TENTACLES_PACKAGE_LOCATION
        self.tentacles_requirements = None
        self.tentacle_group = self.name
        self.in_dev_mode = False
        self.metadata = {}

    async def initialize(self):
        async with aiofiles.open(path.join(self.tentacle_path, self.name,
                                           constants.TENTACLE_METADATA), "r") as metadata_file:
            self._read_metadata_dict(json.loads(await metadata_file.read()))

    def sync_initialize(self):
        try:
            with open(path.join(self.tentacle_path, self.name, constants.TENTACLE_METADATA), "r") as metadata_file:
                self._read_metadata_dict(json.loads(metadata_file.read()))
        except FileNotFoundError:
            pass


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

    def _read_metadata_dict(self, metadata):
        self.metadata = metadata
        self.version = self.metadata[constants.METADATA_VERSION]
        self.origin_package = self.metadata[constants.METADATA_ORIGIN_PACKAGE]
        self.tentacle_class_names = self.metadata[constants.METADATA_TENTACLES]
        self.tentacles_requirements = self.metadata[constants.METADATA_TENTACLES_REQUIREMENTS]
        # self.tentacle_group is this tentacle name if no provided
        self.tentacle_group = self.metadata.get(constants.METADATA_TENTACLES_GROUP, self.name)
        if constants.METADATA_DEV_MODE in self.metadata:
            self.in_dev_mode = self.metadata[constants.METADATA_DEV_MODE]

    @staticmethod
    def _parse_requirements(requirement):
        if constants.TENTACLE_REQUIREMENT_VERSION_EQUALS in requirement:
            return requirement.split(constants.TENTACLE_REQUIREMENT_VERSION_EQUALS)
        else:
            return [requirement, None]
