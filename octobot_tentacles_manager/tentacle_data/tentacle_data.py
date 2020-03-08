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
from importlib import import_module
from os.path import join, sep

from octobot_commons.logging.logging_util import get_logger


class TentacleData:
    def __init__(self, reference_path, name, tentacle_type):
        self.reference_path = reference_path
        self.name = name
        self.tentacle_type = tentacle_type
        self.tentacle_path = join(self.reference_path, self.tentacle_type)
        self.module_import_path = self.tentacle_path.replace(sep, ".")
        self.version = None
        self.origin_package = None
        self.requirements = None

    def load_metadata(self):
        try:
            module_import_path = self.to_import_path(self.tentacle_path)
            tentacle_module = import_module(f".{self.name}", module_import_path)
            self.version = tentacle_module.VERSION
            self.origin_package = tentacle_module.ORIGIN_PACKAGE
            self.requirements = tentacle_module.REQUIREMENTS
        except ModuleNotFoundError as e:
            get_logger(self.__class__.__name__).exception(e, True, f"Error when importing new tentacle module {e}")

    @staticmethod
    def to_import_path(path):
        return path.replace(sep, ".")

    def is_valid(self):
        return self.version is not None

    def __str__(self):
        str_rep = f"{self.name} tentacle [type: {self.tentacle_type}"
        if self.is_valid():
            return f"{str_rep}, version: {self.version}]"
        else:
            return f"{str_rep}]"
