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
from os.path import join

from octobot_tentacles_manager.constants import TENTACLES_PATH, TENTACLE_RESOURCES, DOCUMENTATION_EXT
from octobot_tentacles_manager.tentacle_data.tentacle_data import TentacleData
from octobot_tentacles_manager.util.tentacle_explorer import load_tentacle_with_metadata

# tentacle_data_by_tentacle_class is used to cache tentacles metadata
_tentacle_data_by_tentacle_class = None


async def reload_tentacle_data_by_tentacle_class():
    global _tentacle_data_by_tentacle_class
    loaded_tentacle_data = await load_tentacle_with_metadata(TENTACLES_PATH)
    _tentacle_data_by_tentacle_class = {
        klass: tentacle_data
        for tentacle_data in loaded_tentacle_data
        for klass in tentacle_data.tentacles
    }


def get_resources_path(klass) -> str:
    return join(get_tentacle_module_path(klass), TENTACLE_RESOURCES)


def get_tentacle_module_path(klass) -> str:
    tentacle_data = get_tentacle_data(klass)
    return join(tentacle_data.tentacle_path, tentacle_data.name)


def get_documentation_file_path(klass) -> str:
    return join(get_resources_path(klass), f"{klass.get_name()}{DOCUMENTATION_EXT}")


def get_tentacle_data(klass) -> TentacleData:
    try:
        return _tentacle_data_by_tentacle_class[klass.get_name()]
    except TypeError:
        raise RuntimeError(f"tentacle_data have not been initialized, call reload_tentacle_data_by_tentacle_class "
                           f"fix this issue")
