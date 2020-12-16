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

import octobot_tentacles_manager.models.artifact as artifact


class TentacleBundle(artifact.Artifact):
    def __init__(self, name):
        super().__init__(name)
        self.artifacts = []

    def __str__(self):
        str_rep = f"{self.name} tentacle bundle ["
        if self.is_valid():
            return f"version: {self.version}]"
        else:
            return f"{str_rep}]"
