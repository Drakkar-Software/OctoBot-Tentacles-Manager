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
from octobot_tentacles_manager.loaders.tentacle_loading import reload_tentacle_by_tentacle_class
from octobot_tentacles_manager.managers.tentacles_setup_manager import TentaclesSetupManager


def load_tentacles(verbose=True) -> bool:
    return TentaclesSetupManager.is_tentacles_arch_valid(verbose=verbose)


def reload_tentacle_info() -> None:
    reload_tentacle_by_tentacle_class()
