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

import octobot_commons.logging as logging

import octobot_tentacles_manager.api as api
import octobot_tentacles_manager.api.updater as updater_api
import octobot_tentacles_manager.api.installer as installer_api
import octobot_tentacles_manager.api.uninstaller as uninstaller_api
import octobot_tentacles_manager.constants as constants
import octobot_tentacles_manager


async def _handle_package_manager_command(starting_args,
                                          tentacles_url,
                                          target_dir,
                                          bot_install_dir,
                                          single_tentacle_path,
                                          single_tentacle_type,
                                          export_tentacles_output,
                                          packed_tentacles_output,
                                          quite_mode,
                                          cythonize) -> int:
    error_count = 0
    LOGGER = logging.get_logger(f"{octobot_tentacles_manager.PROJECT_NAME}-CLI")
    async with aiohttp.ClientSession() as aiohttp_session:
        include_dev_mode = starting_args.include_dev_mode
        if starting_args.creator:
            error_count = api.start_tentacle_creator({}, starting_args.creator)
        elif starting_args.repair:
            error_count = await api.repair_installation(bot_path=target_dir)
        elif starting_args.export:
            error_count = await api.create_tentacles_package(export_tentacles_output, target_dir,
                                                             in_zip=False, with_dev_mode=include_dev_mode,
                                                             cythonize=cythonize)
        elif starting_args.pack:
            error_count = await api.create_tentacles_package(packed_tentacles_output, target_dir,
                                                             in_zip=True, with_dev_mode=include_dev_mode,
                                                             cythonize=cythonize)
        elif single_tentacle_path:
            error_count = await api.install_single_tentacle(single_tentacle_path,
                                                            single_tentacle_type,
                                                            bot_path=target_dir,
                                                            aiohttp_session=aiohttp_session,
                                                            bot_install_dir=bot_install_dir)
        elif not (starting_args.all or starting_args.tentacle_names):
            LOGGER.error("Please provide at least one tentacle name or add the '--all' parameter")
            return 1
        elif starting_args.install:
            if tentacles_url is None:
                LOGGER.error("Please provide a tentacle path or URL")
                return 1
            if starting_args.all:
                error_count = await api.install_all_tentacles(tentacles_url,
                                                              bot_path=target_dir,
                                                              aiohttp_session=aiohttp_session,
                                                              quite_mode=quite_mode,
                                                              bot_install_dir=bot_install_dir)
            else:
                error_count = await api.install_tentacles(starting_args.tentacle_names,
                                                          tentacles_url,
                                                          bot_path=target_dir,
                                                          aiohttp_session=aiohttp_session,
                                                          quite_mode=quite_mode,
                                                          bot_install_dir=bot_install_dir)
        elif starting_args.update:
            if tentacles_url is None:
                LOGGER.error("Please provide a tentacle path or URL")
                return 1
            if starting_args.all:
                error_count = await api.update_all_tentacles(tentacles_url,
                                                             bot_path=target_dir,
                                                             aiohttp_session=aiohttp_session,
                                                             quite_mode=quite_mode)
            else:
                error_count = await api.update_tentacles(starting_args.tentacle_names,
                                                         tentacles_url,
                                                         bot_path=target_dir,
                                                         aiohttp_session=aiohttp_session,
                                                         quite_mode=quite_mode)
        elif starting_args.uninstall:
            if starting_args.all:
                error_count = await api.uninstall_all_tentacles(bot_path=target_dir,
                                                                use_confirm_prompt=starting_args.force,
                                                                quite_mode=quite_mode)
            else:
                error_count = await api.uninstall_tentacles(starting_args.tentacle_names,
                                                            bot_path=target_dir,
                                                            use_confirm_prompt=starting_args.force,
                                                            quite_mode=quite_mode)
    if error_count > 0:
        LOGGER.error(f"{error_count} errors occurred while processing tentacles.")
        return 1
    return 0


def handle_tentacles_manager_command(starting_args,
                                     tentacles_url=None,
                                     single_tentacle_path=None,
                                     single_tentacle_type=None,
                                     export_tentacles_output=None,
                                     packed_tentacles_output=None,
                                     bot_install_dir=constants.DEFAULT_BOT_INSTALL_DIR) -> int:
    tentacles_url = starting_args.location[0] if starting_args.location else tentacles_url
    target_bot_dir = starting_args.directory[0] if starting_args.directory else constants.DEFAULT_BOT_PATH
    if starting_args.single_tentacle_install:
        single_tentacle_path = starting_args.single_tentacle_install[0]
        single_tentacle_type = starting_args.single_tentacle_install[1]
    export_tentacles_output = starting_args.export[0] if starting_args.export else export_tentacles_output
    packed_tentacles_output = starting_args.pack[0] if starting_args.pack else packed_tentacles_output
    return asyncio.run(_handle_package_manager_command(starting_args,
                                                       tentacles_url,
                                                       target_bot_dir,
                                                       bot_install_dir,
                                                       single_tentacle_path,
                                                       single_tentacle_type,
                                                       export_tentacles_output,
                                                       packed_tentacles_output,
                                                       starting_args.quite,
                                                       starting_args.cythonize))


def register_tentacles_manager_arguments(tentacles_parser) -> None:
    tentacles_parser.add_argument("-i", "--install", help=installer_api.USER_HELP, action='store_true')
    tentacles_parser.add_argument("-u", "--update", help=updater_api.USER_HELP, action='store_true')
    tentacles_parser.add_argument("-ui", "--uninstall", help=uninstaller_api.USER_HELP, action='store_true')
    tentacles_parser.add_argument("-r", "--repair", help="Repair a tentacles installation. "
                                                         "Fixes __init__.py files, missing main folders "
                                                         "and configuration files.", action='store_true')
    tentacles_parser.add_argument("-sti", "--single-tentacle-install", help='Single tentacle to install identified by '
                                                                            'a local path and its tentacle type.\n'
                                                                            'Example: -sti "/bot/macd_eval" '
                                                                            '"Evaluator/TA".',
                                  nargs=2)
    tentacles_parser.add_argument("-p", "--pack", help="Create a tentacle package containing all tentacles "
                                                       "in the given folder.\n"
                                                       "Specify source folder using the --directory argument.\n"
                                                       "Add --cythonize to cythonize and compile the packed tentacles."
                                                       "Example: -p myTentaclesPackage.zip -d ./tentacles", nargs=1)
    tentacles_parser.add_argument("-e", "--export", help="Export tentacles into a folder containing all tentacles "
                                                         "in the given folder. Removes installation generated files. "
                                                         "Specify source folder using the --directory argument.\n"
                                                         "Example: -e myTentaclesFolder -d ./tentacles", nargs=1)
    tentacles_parser.add_argument("-a", "--all", help="Apply command to all available Tentacles.", action='store_true')
    tentacles_parser.add_argument("-d", "--directory", help=f"Path to the root of the OctoBot installation folder "
                                                            f"to operate on. Default is '{constants.DEFAULT_BOT_PATH}'.",
                                  nargs=1)
    tentacles_parser.add_argument("-l", "--location", help="Tentacles package local path or url to find the "
                                                           "tentacles package to process.", nargs=1)
    tentacles_parser.add_argument("-f", "--force", help="Skip user confirmations.", action='store_true')
    tentacles_parser.add_argument("-idm", "--include-dev-mode", help="Include tentacles in dev mode in export and "
                                                                     "pack commands.", action='store_true')
    tentacles_parser.add_argument("-c", "--creator", help="Start OctoBot Tentacles Creator.\n Examples: -c Evaluator "
                                                          "to create a new evaluator tentacles. Use: -c help to get the"
                                                          " Tentacle Creator help.", nargs='+')
    tentacles_parser.add_argument("-cy", "--cythonize", help="Option for the --pack command: cythonize and "
                                                             "compile the packed tentacles.", action='store_true')
    tentacles_parser.add_argument("-q", "--quite", help="Only display errors in logs.", action='store_true')
    tentacles_parser.add_argument("tentacle_names", nargs="*")


def main():
    parser = argparse.ArgumentParser(description=f"{octobot_tentacles_manager.PROJECT_NAME}-CLI")
    register_tentacles_manager_arguments(parser)
    args = parser.parse_args(sys.argv[1:])
    sys.exit(handle_tentacles_manager_command(args))


if __name__ == "__main__":
    main()
