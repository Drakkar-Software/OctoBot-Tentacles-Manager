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
import asyncio
import logging

from poc import parse_pip_command_result, list_installed_tentacles, install_tentacle, update_tentacle

tentacles_folder = "./tentacles"


async def list_tentacles():
    stdout_list = await list_installed_tentacles(tentacles_folder)
    for stdout, stderr in stdout_list:
        print(parse_pip_command_result(stdout))


async def install_test_tentacle():
    stdout, stderr = await install_tentacle(tentacles_folder, "OctoBot-Commons")
    print(parse_pip_command_result(stdout))


async def update_test_tentacle():
    stdout, stderr = await update_tentacle(tentacles_folder, "OctoBot-Commons")
    print(parse_pip_command_result(stdout))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)

    main_loop.run_until_complete(list_tentacles())
    main_loop.run_until_complete(install_test_tentacle())
    main_loop.run_until_complete(update_test_tentacle())
