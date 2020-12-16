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

import os.path as path

import octobot_tentacles_manager.constants as constants


class TentacleFilter:
    def __init__(self, full_tentacles_list, tentacles_white_list):
        self.tentacles_white_list = tentacles_white_list
        self.full_tentacles_list = full_tentacles_list
        self.tentacle_paths_black_list = [] if self.tentacles_white_list is None else [
            path.join(tentacle.tentacle_path, tentacle.name)
            for tentacle in self.full_tentacles_list
            if tentacle not in self.tentacles_white_list
        ]
        self.ignored_elements = constants.TENTACLES_PACKAGE_IGNORED_ELEMENTS

    def should_ignore(self, folder_path, names):
        return [name
                for name in names
                if self._should_ignore(folder_path, name)]

    def _should_ignore(self, element_path, element_name):
        if element_name in self.ignored_elements:
            return True
        if self.tentacles_white_list is not None:
            candidate_path = path.join(element_path, element_name)
            return path.isdir(candidate_path) and candidate_path in self.tentacle_paths_black_list
        return False
