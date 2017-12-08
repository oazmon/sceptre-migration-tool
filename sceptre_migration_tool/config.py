# -*- coding: utf-8 -*-

"""
sceptre_migration_tool.config

This module imports an AWS stack configuration into Sceptre.
"""

from __future__ import print_function
import os
import yaml
import logging

from .exceptions import ImportFailureError


def default_ctor(loader, tag_suffix, node):
    return tag_suffix + ' ' + str(node.value)


yaml.add_multi_constructor('!', default_ctor)


def import_config(
        migration_environment,
        aws_stack_name,
        config_path,
        template
):

    abs_config_path = os.path.join(
        migration_environment.environment_config.sceptre_dir,
        'config',
        config_path + ".yaml"
    )

    if os.path.isfile(config_path):
        raise ImportFailureError(
            "Unable to import config. "
            "File already exists: file = {}".format(abs_config_path)
        )

    response = migration_environment.connection_manager.call(
        service='cloudformation',
        command='describe_stacks',
        kwargs={
            'StackName': aws_stack_name
        }
    )

    migration_environment.set_resolution_context(
        config_path,
        aws_stack_name,
        response['Stacks'][0],
        template
    )

    with open(abs_config_path, 'w') as config_fobj:
        writer = ConfigFileWriter(
            config_fobj,
            migration_environment
        )
        writer.write()


class ConfigFileWriter(object):
    def __init__(self, config_fobj, migration_environment):
        self.logger = logging.getLogger(__name__)
        self.config_fobj = config_fobj
        self.migration_environment = migration_environment
        self.aws_stack = migration_environment.aws_stack

    def write(self):
        self._write_template_path()
        self._write_stack_name()
        self._write_protect()
        self._write_role_arn()
        self._write_parameters()
        self._write_stack_tags()

    def _write_template_path(self):
        print(
            'template_path: ' +
            self.migration_environment.template.relative_template_path,
            file=self.config_fobj
        )

    def _write_stack_name(self):
        print(
            'stack_name: ' + self.migration_environment.aws_stack_name,
            file=self.config_fobj
        )

    def _write_protect(self):
        if 'EnableTerminationProtection' in self.aws_stack \
                and self.aws_stack['EnableTerminationProtection']:
            print('protect: True', file=self.config_fobj)

    def _write_role_arn(self):
        if 'RoleARN' in self.aws_stack and self.aws_stack['RoleARN']:
            print(
                'role_arn: ' + self.aws_stack['RoleARN'],
                file=self.config_fobj
            )

    def _get_template_parameters(self):
        # we use YAML only as JSON is a subset
        template_body = yaml.load(self.migration_environment.template.body)
        return template_body['Parameters'] \
            if 'Parameters' in template_body else {}

    def _write_parameters(self):
        if 'Parameters' in self.aws_stack and self.aws_stack['Parameters']:
            print('parameters:', file=self.config_fobj)
            template_parameters = self._get_template_parameters()
            aws_stack_parameter_list = sorted(
                self.aws_stack['Parameters'],
                key=lambda x: x['ParameterKey']
            )
            for parameter in aws_stack_parameter_list:
                key = parameter['ParameterKey']
                value = parameter['ParameterValue']
                template_parameter = template_parameters[key]
                if 'Default' in template_parameter \
                        and value == template_parameter['Default']:
                    print(
                        "  #{}: '{}'".format(key, value),
                        file=self.config_fobj
                    )
                else:
                    suggested_value = \
                        self.migration_environment.suggest(value)
                    print(
                        "  {}: '{}'".format(key, suggested_value),
                        file=self.config_fobj
                    )

    def _write_stack_tags(self):
        if 'Tags' in self.aws_stack and len(self.aws_stack['Tags']) > 0:
            print('stack_tags:', file=self.config_fobj)
            for tag in self.aws_stack['Tags']:
                print(
                    '  "{}": "{}"'.format(
                        tag['Key'],
                        tag['Value']
                    ),
                    file=self.config_fobj
                )
