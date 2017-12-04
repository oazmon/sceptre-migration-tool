# -*- coding: utf-8 -*-

"""
sceptre_migration_tool.importer.stack

This module imports a Stack class from AWS.

"""

import logging

from sceptre.stack import Stack

from sceptre_migration_tool.config import import_config
from sceptre_migration_tool.template import import_template


logger = logging.getLogger(__name__)


def import_stack(
        reverse_resolution_service,
        aws_stack_name,
        template_path,
        config_path):

    template = import_template(
        reverse_resolution_service,
        aws_stack_name,
        template_path
    )

    logger.info("%s - Imported AWS CloudFormation template into '%s'"
                " into '%s'", config_path, aws_stack_name, template_path)

    import_config(
        reverse_resolution_service,
        aws_stack_name,
        config_path,
        template
    )

    logger.info(
        "%s - Imported stack config from AWS CloudFormation stack '%s' ",
        config_path,
        aws_stack_name
    )

    return Stack(
            name=config_path,
            environment_config=reverse_resolution_service.environment_config,
            connection_manager=reverse_resolution_service.connection_manager
        )
