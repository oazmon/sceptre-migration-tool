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


import_stack_list = []


def import_stack(env, aws_stack_name, sceptre_stack_path, template_path):
    config_path = "/".join([env.path, sceptre_stack_path])

    logger = logging.getLogger(__name__)
    logger.info("%s - Importing stack", config_path)

    migration_environment = _create_migration_environment(env)

    stack.import_stack(
        migration_environment=migration_environment,
        aws_stack_name=aws_stack_name,
        template_path=template_path,
        config_path=config_path
    )

    logger.info("%s - Stack imported", config_path)


def import_env(env):
    logger = logging.getLogger(__name__)
    logger.info("%s - Importing environment", env.path)

    migration_environment = _create_migration_environment(env)

    describe_stacks_kwargs = {}
    while True:
        response = migration_environment.connection_manager.call(
            service='cloudformation',
            command='describe_stacks',
            kwargs=describe_stacks_kwargs
        )
        for aws_stack in response['Stacks']:
            stack.import_stack(
                migration_environment=migration_environment,
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


def _ensure_env_dir_exists(sceptre_dir, env_path):
    abs_path = os.path.join(
        sceptre_dir,
        env_path.replace("\\", "/")
    )
    if(not os.path.isdir(abs_path)):
        os.makedirs(abs_path)


def import_list(sceptre_dir, options, list_fobj):
    logger = logging.getLogger(__name__)
    logger.info("Importing from list")

    global import_stack_list
    import_stack_list = MigrationEnvironment.read_import_stack_list(list_fobj)

    for item in import_stack_list:
        import_stack(
            Environment(
                sceptre_dir=sceptre_dir,
                environment_path=item[MigrationEnvironment.PART_ENV],
                options=options
            ),
            item[MigrationEnvironment.PART_AWS_STACK_NAME],
            item[MigrationEnvironment.PART_SCEPTRE_STACK_NAME],
            item[MigrationEnvironment.PART_TEMPLATE_PATH]
        )


def generate_import_list(env, list_file_obj=sys.stdout):
    logger = logging.getLogger(__name__)
    logger.info("Generating Import List")

    migration_environment = _create_migration_environment(env)

    describe_stacks_kwargs = {}
    while True:
        response = migration_environment.connection_manager.call(
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


def _create_migration_environment(env):
    env_config = env._get_config()

    connection_manager = ConnectionManager(
        region=env_config.get("region"),
        iam_role=env_config.get("iam_role"),
        profile=env_config.get("profile")
    )

    migration_environment = \
        MigrationEnvironment(connection_manager, env_config, import_stack_list)

    return migration_environment
