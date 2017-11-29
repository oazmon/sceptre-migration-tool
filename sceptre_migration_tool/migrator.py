# -*- coding: utf-8 -*-

"""
sceptre_migration_tool.importer.environment

This module imports config and templates from
AWS for a given stack or environment.

"""

import os

import sceptre_migration_tool.stack as stack
from sceptre.connection_manager import ConnectionManager


def import_stack(env, aws_stack_name, sceptre_stack_path, template_path):
    connection_manager = ConnectionManager(
        region=env._get_config().get("region"),
        iam_role=env._get_config().get("iam_role"),
        profile=env._get_config().get("profile")
    )

    stack.import_stack(
        environment_config=env._get_config(),
        connection_manager=connection_manager,
        aws_stack_name=aws_stack_name,
        template_path=template_path,
        config_path="/".join([env.path, sceptre_stack_path])
    )


def import_env(env):
    env_config = env._get_config()

    connection_manager = ConnectionManager(
        region=env_config.get("region"),
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
                config_path="/".join([env.path, aws_stack['StackName']])
            )
        if 'NextToken' not in response or not response['NextToken']:
            break
        describe_stacks_kwargs['NextToken'] = response['NextToken']
