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
import octobot_tentacles_manager.exporters as exporters
import octobot_tentacles_manager.models as models
import octobot_tentacles_manager.util as util


def start_tentacle_creator(config, commands) -> int:
    tentacle_creator_inst = tentacle_creator.TentacleCreator(config)
    return tentacle_creator_inst.parse_commands(commands)


async def create_tentacles_package(package_name,
                                   tentacles_folder=constants.TENTACLES_PATH,
                                   exported_tentacles_package=None,
                                   in_zip=True,
                                   with_dev_mode=False,
                                   cythonize=False) -> int:
    return await exporters.TentaclePackageExporter(artifact=models.TentaclePackage(package_name),
                                                   tentacles_folder=tentacles_folder,
                                                   exported_tentacles_package=exported_tentacles_package,
                                                   should_zip=in_zip,
                                                   with_dev_mode=with_dev_mode,
                                                   should_cythonize=cythonize).export()


async def create_all_tentacles_bundle():
    tentacles = util.load_tentacle_with_metadata(self.tentacles_folder)
