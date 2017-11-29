# -*- coding: utf-8 -*-

"""
sceptre_migration_tool.config

This module imports an AWS stack configuration into Sceptre.
"""

from __future__ import print_function
import os
import yaml

from .exceptions import ImportFailureError


def import_config(
        template,
        connection_manager,
        aws_stack_name,
        config_path):
    config_path += ".yaml"

    if os.path.isfile(config_path):
        raise ImportFailureError(
            "Unable to import config. "
            "File already exists: file = {}".format(config_path)
        )

    response = connection_manager.call(
        service='cloudformation',
        command='describe_stacks',
        kwargs={
            'StackName': aws_stack_name
        }
    )

    with open(config_path, 'w') as config_file:
        print(
            'template_path: ' + template.relative_template_path,
            file=config_file
        )
        print(
            'stack_name: ' + aws_stack_name,
            file=config_file
        )

        if 'EnableTerminationProtection' in response['Stacks'][0] \
                and response['Stacks'][0]['EnableTerminationProtection']:
            print('protect: True', file=config_file)

        if 'RoleARN' in response['Stacks'][0] \
                and response['Stacks'][0]['RoleARN']:
            print(
                'role_arn: ' + response['Stacks'][0]['RoleARN'],
                file=config_file
            )

        if 'Parameters' in response['Stacks'][0] \
                and response['Stacks'][0]['Parameters']:
            # we use YAML only as JSON is a subset
            def default_ctor(loader, tag_suffix, node):
                return tag_suffix + ' ' + str(node.value)
            yaml.add_multi_constructor('', default_ctor)
            template_body = yaml.load(template.body)

            print('parameters:', file=config_file)
            parameter_list = sorted(
                response['Stacks'][0]['Parameters'],
                key=lambda x: x['ParameterKey']
            )
            template_parameters = template_body['Parameters'] \
                if 'Parameters' in template_body else {}
            for parameter in parameter_list:
                key = parameter['ParameterKey']
                value = parameter['ParameterValue']
                # parameter is always defined in template,
                # otherwise stack would not create
                template_key = template_parameters[key]
                if 'Default' not in template_key \
                        or value != template_key['Default']:
                    print('  {}: {}'.format(key, value), file=config_file)
                else:
                    print('  #{}: {}'.format(key, value), file=config_file)

        if 'Tags' in response['Stacks'][0] \
                and len(response['Stacks'][0]['Tags']) > 0:
            print('stack_tags:', file=config_file)
            for tag in response['Stacks'][0]['Tags']:
                print(
                    '  {}: {}'.format(
                        tag['Key'],
                        tag['Value']
                    ),
                    file=config_file
                )
