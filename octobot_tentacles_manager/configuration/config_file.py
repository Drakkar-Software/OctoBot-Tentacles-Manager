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

import octobot_commons.configuration as configuration
import octobot_commons.json_util as json_util


def read_config(config_file: str, raise_errors: bool = True) -> dict:
    if path.exists(config_file):
        return json_util.read_file(config_file, raise_errors=raise_errors, on_error_value={})
    return {}


def write_config(config_file: str, content: dict) -> None:
    # create config content before opening file not to clear file or json dump exception
    config_content = configuration.dump_formatted_json(content)
    with open(config_file, "w+") as config_file_w:
        config_file_w.write(config_content)
