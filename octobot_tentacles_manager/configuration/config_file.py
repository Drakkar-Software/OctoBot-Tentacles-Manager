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
import aiofiles
from os.path import exists

from octobot_commons.config_manager import dump_json


async def read_config(config_file: str) -> dict:
    if exists(config_file):
        async with aiofiles.open(config_file, "r") as config_file_r:
            return json.loads(await config_file_r.read())
    return {}


def sync_read_config(config_file: str) -> dict:
    if exists(config_file):
        with open(config_file, "r") as config_file_r:
            return json.loads(config_file_r.read())
    return {}


async def write_config(config_file: str, content: dict) -> None:
    async with aiofiles.open(config_file, "w+") as config_file_w:
        await config_file_w.write(dump_json(content))


def sync_write_config(config_file: str, content: dict) -> None:
    with open(config_file, "w+") as config_file_w:
        config_file_w.write(dump_json(content))
