# TODO

import fileinput
import re
import sys
from os import remove

from tentacles_manager.tentacle_manager import TentacleManager
from tentacles_manager.tentacle_util import delete_tentacles_arch
from tentacles_manager.tentacle_package_util import read_tentacles
from tentacles_manager import TENTACLES_PATH, TENTACLES_EVALUATOR_PATH, TENTACLES_EVALUATOR_STRATEGIES_PATH, \
    EVALUATOR_DEFAULT_FOLDER, TENTACLE_MODULE_VERSION, EVALUATOR_CONFIG_FOLDER


# Warning: limit github calls with using install all as little as possible (use install momentum_evaluator instead)


def test_import():
    TentacleManager({})


def test_install_default_branch():
    manager = TentacleManager({})
    _install_test_tentacle(manager)
    _cleanup()


def test_config_file_management():
    manager = TentacleManager({})
    _install_test_tentacle(manager)
    test_tentacle = "staggered_orders_strategy_evaluator"
    tentacle_evaluator_path = f"{TENTACLES_PATH}/{TENTACLES_EVALUATOR_PATH}/{TENTACLES_EVALUATOR_STRATEGIES_PATH}"
    tentacle_path = f"{tentacle_evaluator_path}/{EVALUATOR_DEFAULT_FOLDER}"
    tentacle_name = f"{test_tentacle}.py"

    # change tentacle version to 0 to force update
    _change_tentacle_version(f"{tentacle_path}/{tentacle_name}")
    tentacle_desc = {}
    read_tentacles(tentacle_path, tentacle_desc)
    assert tentacle_desc[test_tentacle][TENTACLE_MODULE_VERSION] == "0.0.0"

    # edit tentacle configuration file
    tentacle_config_file = f"{tentacle_evaluator_path}/{EVALUATOR_CONFIG_FOLDER}" \
        f"/StaggeredOrdersStrategiesEvaluator.json"
    original_config_content = _get_file_content(tentacle_config_file)
    _change_tentacle_config_file(tentacle_config_file)
    edited_config_content = _get_file_content(tentacle_config_file)

    command_update = ["update", test_tentacle]
    manager.parse_commands(command_update, force=True)

    # ensure tentacle got updated
    read_tentacles(tentacle_path, tentacle_desc)
    assert tentacle_desc[test_tentacle][TENTACLE_MODULE_VERSION] != "0.0.0"

    # ensure tentacle configuration file did not change with update
    new_config_content = _get_file_content(tentacle_config_file)
    assert edited_config_content != original_config_content
    assert edited_config_content == new_config_content

    # now check with install command
    _install_test_tentacle(manager)

    # ensure tentacle configuration file did not change with update
    new_config_content = _get_file_content(tentacle_config_file)
    assert edited_config_content == new_config_content

    # now remove config file and ensure install recreates it
    remove(tentacle_config_file)
    _install_test_tentacle(manager)

    # ensure config file got restored
    new_config_content = _get_file_content(tentacle_config_file)
    assert original_config_content == new_config_content

    _cleanup()


def test_install_specified_argument_branch():
    manager = TentacleManager({})
    # use default_git_branch
    command_install = ["install", "all"]
    manager.parse_commands(command_install, force=True, default_git_branch="dev")
    _cleanup()
    # use command_install branch
    command_install = ["install", "momentum_evaluator", "branch", "dev"]
    manager.parse_commands(command_install, force=True, default_git_branch="xyz")
    _cleanup()


def test_install_dev_branch():
    manager = TentacleManager({})
    # command: install all branch dev
    command_install = ["install", "all", "branch", "dev"]
    manager.parse_commands(command_install, force=True)
    _cleanup()
    # command: install all branch=dev
    command_install = ["install", "momentum_evaluator", "branch=dev"]
    manager.parse_commands(command_install, force=True)
    _cleanup()
    # command: install all branch= dev
    command_install = ["install", "momentum_evaluator", "branch=", "dev"]
    manager.parse_commands(command_install, force=True)
    _cleanup()
    # command: install momentum_evaluator trend_evaluator branch dev
    command_install = ["install", "momentum_evaluator", "trend_evaluator", "branch", "dev"]
    manager.parse_commands(command_install, force=True)
    _cleanup()


def _cleanup():
    delete_tentacles_arch()


def _edit_file(file_path, line_pattern, replace_regex, replace_string):
    with fileinput.input(file_path, inplace=True) as f:
        for line in f:
            if line_pattern in line:
                line = re.sub(replace_regex, replace_string, line)
            sys.stdout.write(line)


def _change_tentacle_version(tentacle_path):
    _edit_file(tentacle_path, '"version": "', r"\d", "0")


def _change_tentacle_config_file(file_path):
    _edit_file(file_path, '"required_time_frames" : ', r"\[]", '["1m"]')


def _install_test_tentacle(tentacle_manager):
    command_install = ["install", "staggered_orders_strategy_evaluator"]
    tentacle_manager.parse_commands(command_install, force=True)


def _get_file_content(file_path):
    with open(file_path) as file:
        return file.read()
