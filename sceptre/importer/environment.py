# -*- coding: utf-8 -*-

"""
sceptre.importer.environment

This module imports config and templates from AWS for a given stack or environment.

"""

import os

from sceptre.connection_manager import ConnectionManager
import sceptre.importer.stack as stack


def import_stack(env_config, env_path, aws_stack_name, stack, template_path):
    connection_manager = ConnectionManager(
        region=env_config["region"],
        iam_role=env_config.get("iam_role"),
        profile=env_config.get("profile")
    )

    stack.import_stack(
        environment_config=env_config,
        connection_manager=connection_manager,
        aws_stack_name=aws_stack_name,
        template_path=template_path,
        config_path="/".join([env_path, stack])
    )

def import_env(env_config, env_path):

    connection_manager = ConnectionManager(
        region=env_config["region"],
        iam_role=env_config.get("iam_role"),
        profile=env_config.get("profile")
    )

    describe_stacks_kwargs = {}
    while True:
        response = connection_manager.call(
            service='cloudformation',
            command='describe_stacks',
            kwargs=describe_stacks_kwargs
        )
        for aws_stack in response['Stacks']:
            stack.import_stack(
                environment_config=env_config,
                connection_manager=connection_manager,
                aws_stack_name=aws_stack['StackName'],
                template_path=os.path.join(
                    'templates',
                    'aws-import',
                    aws_stack['StackName'] + '.yaml'
                ),
                config_path="/".join([env_path, aws_stack['StackName']])
            )
        if 'NextToken' not in response or not response['NextToken']:
            break
        describe_stacks_kwargs['NextToken'] = response['NextToken']
