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
from enum import Enum

VERSION = "1.0.5"
PROJECT_NAME = "OctoBot-Tentacles-Manager"
OCTOBOT_NAME = "OctoBot"

# github
GITHUB = "github"
GITHUB_RAW_CONTENT_URL = "https://raw.githubusercontent.com"
GITHUB_API_CONTENT_URL = "https://api.github.com"
GITHUB_BASE_URL = "https://github.com"
GITHUB_ORGANISATION = "Drakkar-Software"
GITHUB_REPOSITORY = f"{GITHUB_ORGANISATION}/{OCTOBOT_NAME}"
GITHUB_URL = f"{GITHUB_BASE_URL}/{GITHUB_REPOSITORY}"

CONFIG_DEBUG_OPTION = "DEV-MODE"

# Tentacles (packages)
PYTHON_INIT_FILE = "__init__.py"
CONFIG_EVALUATOR_FILE = "evaluator_config.json"
CONFIG_TRADING_FILE = "trading_config.json"
TENTACLES_PATH = "tentacles"
TENTACLES_EVALUATOR_PATH = "Evaluator"
TENTACLES_TRADING_PATH = "Trading"
CONFIG_EVALUATOR_FILE_PATH = f"{TENTACLES_PATH}/{TENTACLES_EVALUATOR_PATH}/{CONFIG_EVALUATOR_FILE}"
CONFIG_TRADING_FILE_PATH = f"{TENTACLES_PATH}/{TENTACLES_TRADING_PATH}/{CONFIG_TRADING_FILE}"
CONFIG_DEFAULT_EVALUATOR_FILE = "config/default_evaluator_config.json"
CONFIG_DEFAULT_TRADING_FILE = "config/default_trading_config.json"
TENTACLES_TEST_PATH = "tests"
TENTACLES_EVALUATOR_REALTIME_PATH = "RealTime"
TENTACLES_EVALUATOR_TA_PATH = "TA"
TENTACLES_EVALUATOR_SOCIAL_PATH = "Social"
TENTACLES_EVALUATOR_STRATEGIES_PATH = "Strategies"
TENTACLES_EVALUATOR_UTIL_PATH = "Util"
TENTACLES_TRADING_MODE_PATH = "Mode"
TENTACLES_PYTHON_INIT_CONTENT = "from .Default import *\nfrom .Advanced import *\n"
TENTACLES_PUBLIC_REPOSITORY = f"{GITHUB_ORGANISATION}/{OCTOBOT_NAME}-Tentacles"
TENTACLES_PUBLIC_LIST = "tentacles_list.json"
TENTACLES_DEFAULT_BRANCH = "master"
EVALUATOR_DEFAULT_FOLDER = "Default"
EVALUATOR_ADVANCED_FOLDER = "Advanced"
TENTACLES_INSTALL_FOLDERS = [EVALUATOR_DEFAULT_FOLDER, EVALUATOR_ADVANCED_FOLDER]
EVALUATOR_CONFIG_FOLDER = "config"
EVALUATOR_RESOURCE_FOLDER = "resources"
CONFIG_TENTACLES_KEY = "tentacles-packages"
TENTACLE_PACKAGE_DESCRIPTION = "package_description"
TENTACLE_PACKAGE_DESCRIPTION_LOCALISATION = "localisation"
TENTACLE_PACKAGE_NAME = "name"
TENTACLE_DESCRIPTION_IS_URL = "is_url"
TENTACLE_MODULE_TESTS = "tests"
TENTACLE_MODULE_DESCRIPTION = "$tentacle_description"
TENTACLE_MODULE_REQUIREMENTS = "requirements"
TENTACLE_MODULE_REQUIREMENT_WITH_VERSION = "requirement_with_version"
TENTACLE_MODULE_LIST_SEPARATOR = ","
TENTACLE_MODULE_REQUIREMENT_VERSION_SEPARATOR = "=="
TENTACLE_MODULE_NAME = "name"
TENTACLE_MODULE_TYPE = "type"
TENTACLE_MODULE_SUBTYPE = "subtype"
TENTACLE_MODULE_VERSION = "version"
TENTACLE_MODULE_DEV = "developing"
TENTACLE_PACKAGE = "package_name"
TENTACLE_MODULE_CONFIG_FILES = "config_files"
TENTACLE_MODULE_RESOURCE_FILES = "resource_files"
TENTACLE_CREATOR_PATH = "tentacle_creator"
TENTACLE_TEMPLATE_DESCRIPTION = "description"
TENTACLE_TEMPLATE_PATH = "templates"
TENTACLE_TEMPLATE_PRE_EXT = "_tentacle"
TENTACLE_CONFIG_TEMPLATE_PRE_EXT = "_config"
TENTACLE_TEMPLATE_EXT = ".template"
TENTACLE_CURRENT_MINIMUM_DEFAULT_TENTACLES_VERSION = "1.1.0"

TENTACLE_SONS = {"Social": TENTACLES_EVALUATOR_SOCIAL_PATH,
                 "RealTime": TENTACLES_EVALUATOR_REALTIME_PATH,
                 "Util": TENTACLES_EVALUATOR_UTIL_PATH,
                 "TA": TENTACLES_EVALUATOR_TA_PATH,
                 "Strategies": TENTACLES_EVALUATOR_STRATEGIES_PATH,
                 "Mode": TENTACLES_TRADING_MODE_PATH}

TENTACLE_PARENTS = {
    "Evaluator": TENTACLES_EVALUATOR_PATH,
    "Trading": TENTACLES_TRADING_PATH
}

TENTACLE_TYPES = {**TENTACLE_PARENTS, **TENTACLE_SONS}

# other
CONFIG_FILE_EXT = ".json"


class TentacleManagerActions(Enum):
    INSTALL = 1
    UNINSTALL = 2
    UPDATE = 3
