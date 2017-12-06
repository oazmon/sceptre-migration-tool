# -*- coding: utf-8 -*-

import logging
import os
import re

from sceptre.helpers import get_subclasses

from sceptre_migration_tool.reverse_resolvers import ReverseResolver


class MigrationEnvironment(object):
    def __init__(self, connection_manager, environment_config):
        self.logger = logging.getLogger(__name__)
        self.connection_manager = connection_manager
        self.environment_config = environment_config
        self._reversed_env_config = {
            str(v): "{{ var." + str(k) + " }}"
            for k, v
            in self.environment_config['user_variables'].items()
        }
        self._config_re_pattern = '|'.join(
            [
                re.escape(str(config_value))
                for config_value
                in self.environment_config['user_variables'].values()
            ]
        )
        self._reverse_resolver_list = None

    @property
    def reverse_resolver_list(self):
        if self._reverse_resolver_list is None:
            self._reverse_resolver_list = []
            self._add_reverse_resolvers(
                os.path.join(
                    os.path.dirname(__file__),
                    "reverse_resolvers"
                )
            )
            self._add_reverse_resolvers(
                os.path.join(
                    self.environment_config.sceptre_dir,
                    "reverse_resolvers"
                )
            )
            self._reverse_resolver_list.sort(key=lambda r: r.precendence())
            self.logger.debug(
                "reverse_resolver_list = %s",
                str(self._reverse_resolver_list)
            )
        return self._reverse_resolver_list

    def get_internal_stack(self, stack):
        return None  # TODO

    def _add_reverse_resolvers(self, directory):
        classes = get_subclasses(
            directory=directory, class_type=ReverseResolver
        )
        self.logger.debug(
            "_add_reverse_resolvers for directory %s are %s",
            directory,
            str(classes)
        )
        for node_class in classes.values():
            self._reverse_resolver_list.append(
                node_class(
                    self
                )
            )

    def reverse_resolve(self, value):
        resolution = value
        for reverse_resolver in self.reverse_resolver_list:
            suggestion = reverse_resolver.suggest(value)
            if suggestion:
                resolution = suggestion
                break
        resolution = self._reverse_env_config(resolution)
        self.logger.debug("Resolution for '%s' is '%s'", value, resolution)
        return resolution

    def _reverse_env_config(self, value):
        def reverse(m):
            return self._reversed_env_config[m.group(0)]
        if self._config_re_pattern:
            return re.sub(
                self._config_re_pattern,
                reverse,
                value
            )
        return value
