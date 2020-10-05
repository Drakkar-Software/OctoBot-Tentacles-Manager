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
import aiofiles
import os
import os.path as path


async def find_or_create(path_to_create, is_directory=True, file_content=""):
    if not path.exists(path_to_create):
        if is_directory:
            if not path.isdir(path_to_create):
                os.makedirs(path_to_create)
        else:
            if not path.isfile(path_to_create):
                # should be used for python init.py files only
                async with aiofiles.open(path_to_create, "w+") as file:
                    await file.write(file_content)
        return True
    return False
