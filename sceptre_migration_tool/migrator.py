# -*- coding: utf-8 -*-

"""
sceptre_migration_tool.importer.environment

This module imports config and templates from
AWS for a given stack or environment.

"""

from __future__ import print_function
import os
import logging
import sys

from sceptre.connection_manager import ConnectionManager
from sceptre.environment import Environment
from . import stack
from .migration_environment import MigrationEnvironment


def import_stack(env, aws_stack_name, sceptre_stack_path, template_path):
    config_path = "/".join([env.path, sceptre_stack_path])

    logger = logging.getLogger(__name__)
    logger.info("%s - Importing stack", config_path)

    reverse_resolution_service = _create_reverse_resolution_service(env)

    stack.import_stack(
        reverse_resolution_service=reverse_resolution_service,
        aws_stack_name=aws_stack_name,
        template_path=template_path,
        config_path=config_path
    )

    logger.info("%s - Stack imported", config_path)


def import_env(env):
    logger = logging.getLogger(__name__)
    logger.info("%s - Importing environment", env.path)

    reverse_resolution_service = _create_reverse_resolution_service(env)

    describe_stacks_kwargs = {}
    while True:
        response = reverse_resolution_service.connection_manager.call(
            service='cloudformation',
            command='describe_stacks',
            kwargs=describe_stacks_kwargs
        )
        for aws_stack in response['Stacks']:
            stack.import_stack(
                reverse_resolution_service=reverse_resolution_service,
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

    logger.info("%s - Environment imported", env.path)


def import_list(sceptre_dir, options, list_file):
    logger = logging.getLogger(__name__)
    logger.info("Importing from list: %s", list_file)

    with open(list_file, 'r') as reader:
        for line in reader.readlines():
            if line.startswith('#'):
                next(line)
            parts = line.split()
            if len(parts) < 3:
                next(line)
            import_stack(
                Environment(
                    sceptre_dir=sceptre_dir,
                    environment_path=parts[0],
                    options=options
                ),
                parts[2],
                parts[1],
                parts[3] if len(parts) > 3 else os.path.join(
                        "templates",
                        "aws-import",
                        parts[2] + ".yaml"
                    )
            )


def generate_import_list(env, list_file_obj=sys.stdout):
    logger = logging.getLogger(__name__)
    logger.info("Generating Import List")

    reverse_resolution_service = _create_reverse_resolution_service(env)

    describe_stacks_kwargs = {}
    while True:
        response = reverse_resolution_service.connection_manager.call(
            service='cloudformation',
            command='describe_stacks',
            kwargs=describe_stacks_kwargs
        )
        for aws_stack in response['Stacks']:
            _output_list_line(env.path, aws_stack, list_file_obj)
        if 'NextToken' not in response or not response['NextToken']:
            break
        describe_stacks_kwargs['NextToken'] = response['NextToken']


def _output_list_line(env_path, aws_stack, list_file_obj):
    print(
        env_path,
        aws_stack['StackName'],
        aws_stack['StackName'],
        os.path.join(
            'templates',
            'aws-import',
            aws_stack['StackName'] + '.yaml'
        ),
        file=list_file_obj
    )


def _create_reverse_resolution_service(env):
    env_config = env._get_config()

    connection_manager = ConnectionManager(
        region=env_config.get("region"),
        iam_role=env_config.get("iam_role"),
        profile=env_config.get("profile")
    )

    return MigrationEnvironment(connection_manager, env_config)
