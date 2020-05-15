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

from octobot_commons.logging.logging_util import get_logger
from octobot_tentacles_manager.configuration.config_file import write_config, read_config
from octobot_tentacles_manager.constants import USER_TENTACLE_CONFIG_FILE_PATH, DEFAULT_TENTACLE_CONFIG, \
    ACTIVATABLE_TENTACLES, DEFAULT_BOT_PATH, UNKNOWN_TENTACLES_PACKAGE_LOCATION
from octobot_tentacles_manager.loaders.tentacle_loading import get_tentacle_classes, reload_tentacle_by_tentacle_class


class TentaclesSetupConfiguration:
    TENTACLE_ACTIVATION_KEY = "tentacle_activation"
    REGISTERED_TENTANCLES_KEY = "registered_tentacles"

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
        activatable_tentacles_in_list = [tentacle_class_name
                                         for tentacle in tentacles
                                         if tentacle.get_simple_tentacle_type() in ACTIVATABLE_TENTACLES
                                         for tentacle_class_name in tentacle.tentacle_class_names]
        self._update_tentacles_setup_config(activatable_tentacles_in_list,
                                            default_tentacle_config_file=default_tentacle_config,
                                            remove_missing_tentacles=remove_missing_tentacles)
        if update_location or force_update_registered_tentacles:
            self._update_registered_tentacles(tentacles, update_location)

    def update_activation_configuration(self, new_config, deactivate_other_evaluators, add_missing_elements):
        something_changed = False
        for element_name, activated in new_config.items():
            if element_name in self.tentacles_activation:
                current_activation = self.tentacles_activation[element_name]
                if current_activation != activated:
                    self.logger.info(f"Tentacles configuration updated: {element_name} "
                                     f"{'activated' if activated else 'deactivated'}")
                    self.tentacles_activation[element_name] = activated
                    something_changed = True
            elif add_missing_elements:
                self.tentacles_activation[element_name] = activated
                something_changed = True
        if deactivate_other_evaluators:
            something_changed = self._deactivate_other_evaluators(new_config) or something_changed
        return something_changed

    def _deactivate_other_evaluators(self, new_config):
        something_changed = False
        from octobot_commons.tentacles_management.class_inspector import get_class_from_string, \
            evaluator_parent_inspection
        has_evaluators = True
        try:
            from octobot_evaluators.evaluator.TA_evaluator import TAEvaluator
            from octobot_evaluators.evaluator.social_evaluator import SocialEvaluator
            from octobot_evaluators.evaluator.realtime_evaluator import RealTimeEvaluator
            import tentacles.Evaluator.TA as TA
            import tentacles.Evaluator.Social as SE
            import tentacles.Evaluator.RealTime as RE
        except ImportError:
            has_evaluators = False
        for element_name in self.tentacles_activation.keys():
            if element_name not in new_config:
                if self.tentacles_activation[element_name]:
                    is_evaluator = False
                    if has_evaluators:
                        # deactivate only evaluators
                        ta_klass = get_class_from_string(element_name, TAEvaluator,
                                                         TA, evaluator_parent_inspection)
                        se_klass = get_class_from_string(element_name, SocialEvaluator,
                                                         SE, evaluator_parent_inspection)
                        re_klass = get_class_from_string(element_name, RealTimeEvaluator,
                                                         RE, evaluator_parent_inspection)
                        is_evaluator = any(klass is not None
                                           for klass in [ta_klass, se_klass, re_klass])
                    if is_evaluator:
                        self.logger.info(f"Tentacles configuration updated: {element_name} "
                                         f"{'deactivated'}")
                        self.tentacles_activation[element_name] = False
                        something_changed = True
        return something_changed

    def replace_tentacle_activation(self, new_config):
        self.tentacles_activation = copy(new_config)

    def read_config(self):
        try:
            self._from_dict(read_config(self.config_path))
        except Exception as e:
            self.logger.error(f"Error when reading tentacles global configuration file ({e}), "
                              "resetting this file with default values. This will not change "
                              "any specific tentacle configuration.")
            if get_tentacle_classes() is None:
                reload_tentacle_by_tentacle_class()
            activatable_tentacles_in_list = [tentacle_class_name
                                             for tentacle_class_name, tentacle in get_tentacle_classes().items()
                                             if tentacle.get_simple_tentacle_type() in ACTIVATABLE_TENTACLES]
            self._update_tentacles_setup_config(activatable_tentacles_in_list)
            self.save_config()

    def save_config(self):
        parent_dir, _ = split(self.config_path)
        if not exists(parent_dir):
            makedirs(parent_dir)
        write_config(self.config_path, self._to_dict())

    def _update_tentacles_setup_config(self,
                                       activatable_tentacles_in_list,
                                       default_tentacle_config_file=DEFAULT_TENTACLE_CONFIG,
                                       remove_missing_tentacles=True):

        default_config = read_config(default_tentacle_config_file)
        default_activation_config = default_config[self.TENTACLE_ACTIVATION_KEY] \
            if self.TENTACLE_ACTIVATION_KEY in default_config else {}
        for tentacle in activatable_tentacles_in_list:
            self._update_tentacle_activation(tentacle, default_activation_config)
        if remove_missing_tentacles:
            self._filter_tentacle_activation(activatable_tentacles_in_list)

    def _update_tentacle_activation(self, tentacle, default_config):
        if tentacle not in self.tentacles_activation:
            if tentacle in default_config:
                self.tentacles_activation[tentacle] = default_config[tentacle]
            else:
                self.tentacles_activation[tentacle] = False

    def _filter_tentacle_activation(self, activatable_tentacles_in_list):
        for key in list(self.tentacles_activation.keys()):
            if key not in activatable_tentacles_in_list:
                self.tentacles_activation.pop(key)

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
