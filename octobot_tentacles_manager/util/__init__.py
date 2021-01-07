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

from octobot_tentacles_manager.util import tentacle_fetching
from octobot_tentacles_manager.util import tentacle_explorer
from octobot_tentacles_manager.util import tentacle_filter
from octobot_tentacles_manager.util import tentacle_cleaner
from octobot_tentacles_manager.util import file_util

from octobot_tentacles_manager.util.os_util import (
    get_os_str,
    get_arch_str,
)
from octobot_tentacles_manager.util.tentacle_fetching import (
    cleanup_temp_dirs,
    fetch_and_extract_tentacles,
    get_local_arch_download_path,
)
from octobot_tentacles_manager.util.tentacle_explorer import (
    load_tentacle_with_metadata,
    get_tentacles_from_package,
)
from octobot_tentacles_manager.util.file_util import (
    find_or_create,
    replace_with_remove_or_rename,
    merge_folders,
)
from octobot_tentacles_manager.util.tentacle_filter import (
    TentacleFilter,
    filter_tentacles_by_dev_mode_and_package,
)
from octobot_tentacles_manager.util.tentacle_cleaner import (
    remove_unnecessary_files,
    remove_non_tentacles_files,
    remove_dir_or_file_from_path,
    remove_dir_or_file,
)

__all__ = [
    "cleanup_temp_dirs",
    "remove_dir_or_file",
    "remove_dir_or_file_from_path",
    "fetch_and_extract_tentacles",
    "get_local_arch_download_path",
    "load_tentacle_with_metadata",
    "get_tentacles_from_package",
    "find_or_create",
    "get_tentacles_from_package",
    "replace_with_remove_or_rename",
    "merge_folders",
    "TentacleFilter",
    "remove_unnecessary_files",
    "remove_non_tentacles_files",
    "filter_tentacles_by_dev_mode_and_package",
    "get_arch_str",
    "get_os_str",
]
