# TODO

from tentacles_manager.tentacle_manager import TentacleManager
from tentacles_manager.tentacle_util import delete_tentacles_arch


def _cleanup():
    delete_tentacles_arch()

# Warning: limit github calls with using install all as little as possible (use install momentum_evaluator instead)


def test_import():
    TentacleManager({})


def test_install_default_branch():
    manager = TentacleManager({})
    command_install = ["install", "momentum_evaluator"]
    manager.parse_commands(command_install, force=True)
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
