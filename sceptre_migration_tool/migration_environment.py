# -*- coding: utf-8 -*-

import logging
import os
import re

from sceptre.helpers import get_subclasses

from sceptre_migration_tool.reverse_resolver import ReverseResolver


class MigrationEnvironment(object):
    def __init__(self, connection_manager, environment_config):
        self.logger = logging.getLogger(__name__)
        self.connection_manager = connection_manager
        self.environment_config = environment_config
        self._reversed_env_config = {
            v: "{{ " + k + " }}" for k, v in self.environment_config.items()
        }
        self._config_re_pattern = '|'.join(
            [
                re.escape(config_value)
                for config_value in self.environment_config.values()
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
                    self.environment_config['sceptre_dir'],
                    "reverse_resolvers"
                )
            )
            self._reverse_resolver_list.sort(key=lambda r: r.precendence())
        return self._reverse_resolver_list

    def get_internal_stack(self, stack):
        return None  # TODO

    def _add_reverse_resolvers(self, directory):
        classes = get_subclasses(
            directory=directory, class_type=ReverseResolver
        )
        for node_class in classes.values():
            self._reverse_resolver_list.append(
                node_class(
                    self
                )
            )

    def reverse_resolve(self, value):
        for reverse_resolver in self.reverse_resolver_list:
            suggestion = reverse_resolver.suggest(value)
            if suggestion:
                value = suggestion
                break
        return self._reverse_env_config(value)

    def _reverse_env_config(self, value):
        if self._config_re_pattern:
            return re.sub(
                self._config_re_pattern,
                lambda matchobj: self._reversed_env_config[matchobj.group(0)],
                value
            )
        return value
