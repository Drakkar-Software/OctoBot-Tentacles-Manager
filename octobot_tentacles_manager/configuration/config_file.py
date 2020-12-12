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
import json
import os.path as path

import octobot_commons.configuration as configuration


def read_config(config_file: str) -> dict:
    if path.exists(config_file):
        with open(config_file, "r") as config_file_r:
            return json.loads(config_file_r.read())
    return {}


def write_config(config_file: str, content: dict) -> None:
    # create config content before opening file not to clear file or json dump exception
    config_content = configuration.dump_formatted_json(content)
    with open(config_file, "w+") as config_file_w:
        config_file_w.write(config_content)
