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
from copy import copy
from os import makedirs
from os.path import join, split, exists

from octobot_tentacles_manager.constants import TENTACLES_EVALUATOR_REALTIME_PATH, TENTACLES_EVALUATOR_TA_PATH, \
    TENTACLES_TRADING_MODE_PATH, TENTACLES_EVALUATOR_STRATEGIES_PATH, TENTACLES_EVALUATOR_SOCIAL_PATH
from octobot_commons.logging.logging_util import get_logger
from octobot_tentacles_manager.configuration.config_file import write_config, read_config
from octobot_tentacles_manager.constants import USER_TENTACLE_CONFIG_FILE_PATH, DEFAULT_TENTACLE_CONFIG, \
    DEFAULT_BOT_PATH, UNKNOWN_TENTACLES_PACKAGE_LOCATION, TENTACLES_PATH
from octobot_tentacles_manager.loaders.tentacle_loading import get_tentacle_classes, ensure_tentacles_metadata


class TentaclesSetupConfiguration:
    TENTACLE_ACTIVATION_KEY = "tentacle_activation"
    REGISTERED_TENTANCLES_KEY = "registered_tentacles"
    DEFAULT_DEACTIVATABLE_TENTACLE_SUB_TYPES = {
        TENTACLES_EVALUATOR_REALTIME_PATH,
        TENTACLES_EVALUATOR_TA_PATH,
        TENTACLES_EVALUATOR_SOCIAL_PATH,
        TENTACLES_EVALUATOR_STRATEGIES_PATH,
        TENTACLES_TRADING_MODE_PATH
    }

    def __init__(self, bot_installation_path=DEFAULT_BOT_PATH, config_path=USER_TENTACLE_CONFIG_FILE_PATH):
        self.logger = get_logger(self.__class__.__name__)
        self.config_path = join(bot_installation_path, config_path)
        self.tentacles_activation = {}
        self.registered_tentacles = {}

    def register_tentacles_package(self, package_name, package_location):
        self.registered_tentacles[package_name] = package_location

    def unregister_tentacles_package(self, package_name):
        self.registered_tentacles.pop(package_name)

    async def fill_tentacle_config(self, tentacles, default_tentacle_config=DEFAULT_TENTACLE_CONFIG,
                                   remove_missing_tentacles=True, update_location=None,
                                   force_update_registered_tentacles=False):
        self._update_tentacles_setup_config(tentacles,
                                            default_tentacle_config_file=default_tentacle_config,
                                            remove_missing_tentacles=remove_missing_tentacles)
        if update_location or force_update_registered_tentacles:
            self._update_registered_tentacles(tentacles, update_location)

    def update_activation_configuration(self, new_config, deactivate_other_evaluators,
                                        add_missing_elements, tentacles_path=TENTACLES_PATH):
        something_changed = False
        ensure_tentacles_metadata(tentacles_path)
        for element_name, activated in new_config.items():
            try:
                element_type = get_tentacle_classes()[element_name].tentacle_root_type
                if element_name in self.tentacles_activation[element_type]:
                    current_activation = self.tentacles_activation[element_type][element_name]
                    if current_activation != activated:
                        self.logger.info(f"Tentacles configuration updated: {element_name} "
                                         f"{'activated' if activated else 'deactivated'}")
                        self.tentacles_activation[element_type][element_name] = activated
                        something_changed = True
                elif add_missing_elements:
                    self.tentacles_activation[element_type][element_name] = activated
                    something_changed = True
            except KeyError:
                # tentacle missing in loaded metadata: can't be used
                self.logger.error(f"Impossible to change activation of {element_name}: this Tentacle class is not "
                                  f"in loaded tentacles metadata dict.")
        if deactivate_other_evaluators:
            something_changed = self._deactivate_other_evaluators(new_config) or something_changed
        return something_changed

    def is_tentacle_activated(self, tentacle_class_name, tentacles_path=TENTACLES_PATH):
        ensure_tentacles_metadata(tentacles_path)
        tentacle_type = get_tentacle_classes()[tentacle_class_name].tentacle_root_type
        return self.tentacles_activation[tentacle_type][tentacle_class_name]

    def from_activated_tentacles_classes(self, *tentacles_classes, tentacles_path=TENTACLES_PATH):
        ensure_tentacles_metadata(tentacles_path)
        tentacle_by_class_name = get_tentacle_classes()
        for tentacle_class in tentacles_classes:
            tentacle_name = tentacle_class.get_name()
            tentacle = tentacle_by_class_name[tentacle_name]
            try:
                self.tentacles_activation[tentacle.tentacle_root_type][tentacle_name] = True
            except KeyError:
                self.tentacles_activation[tentacle.tentacle_root_type] = {tentacle_name: True}

    def _deactivate_other_evaluators(self, new_config):
        something_changed = False
        for element_type, element_names in self.tentacles_activation.items():
            for element_name in element_names:
                # for each activated element that is not in new_config
                if element_name not in new_config and self.tentacles_activation[element_type][element_name]:
                    # only handle evaluator tentacles
                    something_changed = self._deactivate_tentacle_if_evaluator(element_name, element_type) or \
                                        something_changed

        return something_changed

    def _deactivate_tentacle_if_evaluator(self, element_name, element_type):
        if get_tentacle_classes()[element_name].get_simple_tentacle_type() in {
            TENTACLES_EVALUATOR_TA_PATH,
            TENTACLES_EVALUATOR_SOCIAL_PATH,
            TENTACLES_EVALUATOR_REALTIME_PATH
        }:
            self.logger.info(f"Tentacles configuration updated: {element_name} {'deactivated'}")
            self.tentacles_activation[element_type][element_name] = False
            return True
        return False

    def replace_tentacle_activation(self, new_config):
        self.tentacles_activation = copy(new_config)

    def read_config(self, tentacles_path=TENTACLES_PATH):
        try:
            self._from_dict(read_config(self.config_path))
        except Exception as e:
            self.logger.error(f"Error when reading tentacles global configuration file ({e}), "
                              "resetting this file with default values. This will not change "
                              "any specific tentacle configuration.")
            ensure_tentacles_metadata(tentacles_path)
            self._update_tentacles_setup_config(get_tentacle_classes().values())
            self.save_config()

    def save_config(self):
        parent_dir, _ = split(self.config_path)
        if not exists(parent_dir):
            makedirs(parent_dir)
        write_config(self.config_path, self._to_dict())

    def _update_tentacles_setup_config(self,
                                       tentacles,
                                       default_tentacle_config_file=DEFAULT_TENTACLE_CONFIG,
                                       remove_missing_tentacles=True):

        default_config = read_config(default_tentacle_config_file)
        default_activation_config = default_config[self.TENTACLE_ACTIVATION_KEY] \
            if self.TENTACLE_ACTIVATION_KEY in default_config else {}
        for tentacle in tentacles:
            self._update_tentacle_activation(tentacle, default_activation_config)
        if remove_missing_tentacles:
            self._filter_tentacle_activation(tentacles)

    def _update_tentacle_activation(self, tentacle, default_config):
        if tentacle.tentacle_root_type not in self.tentacles_activation:
            self.tentacles_activation[tentacle.tentacle_root_type] = {}
        for tentacle_class_name in tentacle.tentacle_class_names:
            if tentacle_class_name not in self.tentacles_activation[tentacle.tentacle_root_type]:
                self._set_activation_using_default_config(tentacle, tentacle_class_name, default_config)

    def _set_activation_using_default_config(self, tentacle, tentacle_class_name, default_config):
        if tentacle.tentacle_root_type in default_config:
            # if tentacle_type in default config: use default value or do not activate (unless
            # if tentacle sub type in DEFAULT_ACTIVATED_TENTACLE_TYPES)
            if tentacle_class_name in default_config[tentacle.tentacle_root_type]:
                self.tentacles_activation[tentacle.tentacle_root_type][tentacle_class_name] = \
                    default_config[tentacle.tentacle_root_type][tentacle_class_name]
            else:
                # activate by default unless the sub type of this tentacle in among the sub types to be deactivated by
                # default
                self.tentacles_activation[tentacle.tentacle_root_type][tentacle_class_name] = \
                    tentacle.get_simple_tentacle_type() not in self.DEFAULT_DEACTIVATABLE_TENTACLE_SUB_TYPES
        else:
            # if tentacle_type not in default config: activate by default
            self.tentacles_activation[tentacle.tentacle_root_type][tentacle_class_name] = True

    def _filter_tentacle_activation(self, tentacles):
        tentacle_names = [tentacle_class_name
                          for tentacle in tentacles
                          for tentacle_class_name in tentacle.tentacle_class_names]
        for element_type, element_names in self.tentacles_activation.items():
            for element_name in list(element_names):
                if element_name not in tentacle_names:
                    self.tentacles_activation[element_type].pop(element_name)

    def _update_registered_tentacles(self, tentacles, update_location):
        packages = set(tentacle.origin_package
                       for tentacle in tentacles)
        for package in packages:
            if package not in self.registered_tentacles:
                self.registered_tentacles[package] = update_location or UNKNOWN_TENTACLES_PACKAGE_LOCATION
        for registered_package in list(self.registered_tentacles):
            if registered_package not in packages:
                self.registered_tentacles.pop(registered_package)

    def _from_dict(self, input_dict):
        if self.TENTACLE_ACTIVATION_KEY in input_dict:
            self.tentacles_activation = input_dict[self.TENTACLE_ACTIVATION_KEY]
        if self.REGISTERED_TENTANCLES_KEY in input_dict:
            self.registered_tentacles = input_dict[self.REGISTERED_TENTANCLES_KEY]

    def _to_dict(self):
        return {
            self.TENTACLE_ACTIVATION_KEY: self.tentacles_activation,
            self.REGISTERED_TENTANCLES_KEY: self.registered_tentacles
        }
