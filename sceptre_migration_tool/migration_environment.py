# -*- coding: utf-8 -*-

import logging
import os
from sceptre.helpers import get_subclasses

from sceptre_migration_tool.reverse_resolver import ReverseResolver


class MigrationEnvironment(object):
    def __init__(self, connection_manager, environment_config):
        self.logger = logging.getLogger(__name__)
        self.connection_manager = connection_manager
        self.environment_config = environment_config
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
        return self._reverse_resolver_list

    def _add_reverse_resolvers(self, directory):
        classes = get_subclasses(
            directory=directory, class_type=ReverseResolver
        )
        for node_class in classes.values():
            self._reverse_resolver_list.append(
                node_class(
                    self.connection_manager,
                    self.environment_config
                )
            )

    def reverse_resolve(self, value):
        for reverse_resolver in self.reverse_resolver_list:
            suggestion = reverse_resolver.suggest(value)
            if suggestion:
                return suggestion
        return value
