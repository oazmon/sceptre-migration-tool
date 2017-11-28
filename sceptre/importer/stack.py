# -*- coding: utf-8 -*-

"""
sceptre.importer.stack

This module imports a Stack class from AWS.

"""

import logging
import os

from sceptre.stack import Stack

from .config import import_config
from .template import import_template


def import_stack(
        environment_config,
        connection_manager,
        aws_stack_name,
        template_path,
        config_path):
    logger = logging.getLogger(__name__)

    abs_template_path = os.path.join(
        environment_config.sceptre_dir,
        template_path
    )

    template = import_template(
        connection_manager,
        aws_stack_name,
        abs_template_path
    )
    template.relative_template_path = template_path

    logger.info("Imported AWS CloudFormation template '{}'"
                " into '{}'".format(aws_stack_name, template_path))

    abs_config_path = os.path.join(
        environment_config.sceptre_dir,
        'config',
        config_path
    )

    import_config(
        template,
        connection_manager,
        aws_stack_name,
        abs_config_path
    )

    logger.info("Imported AWS CloudFormation template '{}' "
                "into 'config/{}'".format(aws_stack_name, config_path))

    return Stack(
            name=config_path,
            environment_config=environment_config,
            connection_manager=connection_manager
        )
