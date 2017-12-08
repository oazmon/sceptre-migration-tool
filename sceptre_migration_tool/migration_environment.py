# -*- coding: utf-8 -*-

import logging
import os
import re

from sceptre.helpers import get_subclasses
from sceptre.template import Template

from sceptre_migration_tool.reverse_resolvers import ReverseResolver


class MigrationEnvironment(object):
    PART_ENV = 0
    PART_SCEPTRE_STACK_NAME = 1
    PART_AWS_STACK_NAME = 2
    PART_TEMPLATE_PATH = 3

    @classmethod
    def read_import_stack_list(cls, list_fobj):
        import_stack_list = []
        for line in list_fobj.readlines():
            item = cls._parse_import_stack_item(line)
            if item:
                import_stack_list.append(item)
        return import_stack_list

    @classmethod
    def _parse_import_stack_item(cls, line):
        if line.startswith('#'):
            return None
        parts = line.split()
        if len(parts) < 3:
            return None
        return (
            parts[cls.PART_ENV],
            parts[cls.PART_SCEPTRE_STACK_NAME],
            parts[cls.PART_AWS_STACK_NAME],
            parts[cls.PART_TEMPLATE_PATH] if len(parts) > 3 else
            os.path.join(
                "templates",
                "aws-import",
                parts[cls.PART_AWS_STACK_NAME] + ".yaml"
            )
        )

    def __init__(self,
                 connection_manager, environment_config, import_stack_list=[]
                 ):
        self.logger = logging.getLogger(__name__)
        self.connection_manager = connection_manager
        self.environment_config = environment_config
        self.import_stack_list = import_stack_list
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
        self.config_path = ""
        self.aws_stack_name = ""
        self.aws_stack = {}
        self.template = Template("", {})

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
        for item in self.import_stack_list:
            if stack == item[self.PART_AWS_STACK_NAME]:
                return "{}/{}".format(
                    item[self.PART_ENV],
                    item[self.PART_SCEPTRE_STACK_NAME]
                )
        return None

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

    def set_resolution_context(
            self, config_path, aws_stack_name, aws_stack, template
    ):
        self.config_path = config_path
        self.aws_stack_name = aws_stack_name
        self.aws_stack = aws_stack
        self.template = template

    def suggest(self, value):
        if value in self._reversed_env_config:
            return self._reversed_env_config[value]
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
