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


def import_config(
        reverse_resolution_service,
        aws_stack_name,
        config_path,
        template
):

    abs_config_path = os.path.join(
        reverse_resolution_service.environment_config.sceptre_dir,
        'config',
        config_path + ".yaml"
    )

    if os.path.isfile(config_path):
        raise ImportFailureError(
            "Unable to import config. "
            "File already exists: file = {}".format(abs_config_path)
        )

    response = reverse_resolution_service.connection_manager.call(
        service='cloudformation',
        command='describe_stacks',
        kwargs={
            'StackName': aws_stack_name
        }
    )

    with open(abs_config_path, 'w') as config_file:
        writer = ConfigFileWriter(
            config_file,
            reverse_resolution_service
        )
        writer.write(
            aws_stack_name,
            response['Stacks'][0],
            template
        )


class ConfigFileWriter(object):
    def __init__(self, config_file, reverse_resolution_service):
        self.config_file = config_file
        self.reverse_resolution_service = reverse_resolution_service
        self.logger = logging.getLogger(__name__)

    def write(self, aws_stack_name, aws_stack, template):
        self.template = template
        self.aws_stack = aws_stack
        self._write_template_path()
        self._write_stack_name(aws_stack_name)
        self._write_protect()
        self._write_role_arn()
        self._write_parameters()
        self._write_stack_tags()

    def _write_template_path(self):
        print(
            'template_path: ' + self.template.relative_template_path,
            file=self.config_file
        )

    def _write_stack_name(self, aws_stack_name):
        print(
            'stack_name: ' + aws_stack_name,
            file=self.config_file
        )

    def _write_protect(self):
        if 'EnableTerminationProtection' in self.aws_stack \
                and self.aws_stack['EnableTerminationProtection']:
            print('protect: True', file=self.config_file)

    def _write_role_arn(self):
        if 'RoleARN' in self.aws_stack and self.aws_stack['RoleARN']:
            print(
                'role_arn: ' + self.aws_stack['RoleARN'],
                file=self.config_file
            )

    def _get_template_parameters(self):
        # we use YAML only as JSON is a subset
        def default_ctor(loader, suffix, node):
            return suffix + ' ' + str(node.value)
        yaml.add_multi_constructor('', default_ctor)
        template_body = yaml.load(self.template.body)
        return template_body['Parameters'] \
            if 'Parameters' in template_body else {}

    def _write_parameters(self):
        if 'Parameters' in self.aws_stack and self.aws_stack['Parameters']:
            print('parameters:', file=self.config_file)
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
                        '  #{}: {}'.format(key, value),
                        file=self.config_file
                    )
                else:
                    print(
                        '  {}: {}'.format(
                            key,
                            self.reverse_resolution_service.reverse_resolve(
                                value
                            )
                        ),
                        file=self.config_file
                    )

    def _write_stack_tags(self):
        if 'Tags' in self.aws_stack and len(self.aws_stack['Tags']) > 0:
            print('stack_tags:', file=self.config_file)
            for tag in self.aws_stack['Tags']:
                print(
                    '  {}: {}'.format(
                        tag['Key'],
                        tag['Value']
                    ),
                    file=self.config_file
                )
