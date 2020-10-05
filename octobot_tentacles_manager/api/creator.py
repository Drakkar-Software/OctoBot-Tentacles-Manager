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
import octobot_tentacles_manager.creators as tentacle_creator
import octobot_tentacles_manager.creators as tentacles_package_creator


def start_tentacle_creator(config, commands) -> int:
    tentacle_creator_inst = tentacle_creator.TentacleCreator(config)
    return tentacle_creator_inst.parse_commands(commands)


async def create_tentacles_package(package_name, tentacles_folder=constants.TENTACLES_PATH,
                                   in_zip=True, with_dev_mode=False, cythonize=False) -> int:
    return await tentacles_package_creator.create_tentacles_package_from_local_tentacles(package_name, tentacles_folder,
                                                                                         in_zip, with_dev_mode,
                                                                                         cythonize)
