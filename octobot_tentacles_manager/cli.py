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
import argparse
import asyncio
import sys
import aiohttp

from octobot_commons.logging.logging_util import get_logger
from octobot_tentacles_manager.api.creator import start_tentacle_creator
from octobot_tentacles_manager.api.installer import install_all_tentacles, install_tentacles, \
    USER_HELP as INSTALL_USER_HELP, install_single_tentacle
from octobot_tentacles_manager.api.uninstaller import uninstall_all_tentacles, uninstall_tentacles, \
    USER_HELP as UNINSTALL_USER_HELP
from octobot_tentacles_manager.api.updater import update_all_tentacles, update_tentacles, \
    USER_HELP as UPDATE_USER_HELP
from octobot_tentacles_manager.constants import DEFAULT_TENTACLES_URL, DEFAULT_BOT_PATH
from octobot_tentacles_manager import PROJECT_NAME


async def _handle_package_manager_command(starting_args, tentacles_url, target_dir,
                                          single_tentacle_path, single_tentacle_type) -> int:
    error_count = 0
    LOGGER = get_logger(f"{PROJECT_NAME}-CLI")
    async with aiohttp.ClientSession() as aiohttp_session:
        if starting_args.creator:
            error_count = start_tentacle_creator({}, starting_args.creator)
        if single_tentacle_path:
            error_count = await install_single_tentacle(single_tentacle_path,
                                                        single_tentacle_type,
                                                        bot_path=target_dir,
                                                        aiohttp_session=aiohttp_session)
        elif not (starting_args.all or starting_args.tentacle_names):
            LOGGER.error("Please provide at least one tentacle name or add the '--all' parameter")
            return 1
        elif starting_args.install:
            if starting_args.all:
                error_count = await install_all_tentacles(tentacles_url,
                                                          bot_path=target_dir,
                                                          aiohttp_session=aiohttp_session)
            else:
                error_count = await install_tentacles(starting_args.tentacle_names,
                                                      tentacles_url,
                                                      bot_path=target_dir,
                                                      aiohttp_session=aiohttp_session)
        elif starting_args.update:
            if starting_args.all:
                error_count = await update_all_tentacles(tentacles_url,
                                                         bot_path=target_dir,
                                                         aiohttp_session=aiohttp_session)
            else:
                error_count = await update_tentacles(starting_args.tentacle_names,
                                                     tentacles_url,
                                                     bot_path=target_dir,
                                                     aiohttp_session=aiohttp_session)
        elif starting_args.uninstall:
            if starting_args.all:
                error_count = await uninstall_all_tentacles(bot_path=target_dir,
                                                            use_confirm_prompt=starting_args.force)
            else:
                error_count = await uninstall_tentacles(starting_args.tentacle_names,
                                                        bot_path=target_dir,
                                                        use_confirm_prompt=starting_args.force)
    if error_count > 0:
        LOGGER.error(f"{error_count} errors occurred while processing tentacles.")
        return 1
    return 0


def handle_tentacles_manager_command(starting_args, tentacles_url=DEFAULT_TENTACLES_URL,
                                     single_tentacle_path=None, single_tentacle_type=None) -> int:
    tentacles_url = starting_args.location[0] if starting_args.location else tentacles_url
    target_bot_dir = starting_args.directory[0] if starting_args.directory else DEFAULT_BOT_PATH
    if starting_args.single_tentacle_install:
        single_tentacle_path = starting_args.single_tentacle_install[0]
        single_tentacle_type = starting_args.single_tentacle_install[1]
    return asyncio.run(_handle_package_manager_command(starting_args, tentacles_url, target_bot_dir,
                                                       single_tentacle_path, single_tentacle_type))


def register_tentacles_manager_arguments(tentacles_parser) -> None:
    tentacles_parser.add_argument("-i", "--install", help=INSTALL_USER_HELP, action='store_true')
    tentacles_parser.add_argument("-u", "--update", help=UPDATE_USER_HELP, action='store_true')
    tentacles_parser.add_argument("-ui", "--uninstall", help=UNINSTALL_USER_HELP, action='store_true')
    tentacles_parser.add_argument("-a", "--all", help="Apply command to all available Tentacles", action='store_true')
    tentacles_parser.add_argument("-f", "--force", help="Skip user confirmations", action='store_true')
    tentacles_parser.add_argument("-l", "--location", help="Tentacles package local path or url to find the "
                                                           "tentacles package to process.", nargs=1)
    tentacles_parser.add_argument("-sti", "--single-tentacle-install", help='Single tentacle to install identified by '
                                                                            'a local path and its tentacle type.\n'
                                                                            'Example: -sti "/bot/macd_eval" '
                                                                            '"Evaluator/TA"',
                                  nargs=2)
    tentacles_parser.add_argument("-d", "--directory", help=f"Path to the root of the octobot installation folder "
                                                            f"to operate on. Default is '{DEFAULT_BOT_PATH}'.",
                                  nargs=1)
    tentacles_parser.add_argument("-c", "--creator", help="Start OctoBot Tentacles Creator.\n Examples: -c Evaluator "
                                                          "to create a new evaluator tentacles. Use: -c help to get the"
                                                          " Tentacle Creator help", nargs='+')
    tentacles_parser.add_argument("tentacle_names", nargs="*")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"{PROJECT_NAME}-CLI")
    register_tentacles_manager_arguments(parser)
    args = parser.parse_args(sys.argv[1:])
    sys.exit(handle_tentacles_manager_command(args))
