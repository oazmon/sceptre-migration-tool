# -*- coding: utf-8 -*-

"""
sceptre_migration_tool.cli

This module implements the Sceptre Migration Tool CLI
"""

import os
import logging
from logging import Formatter
import warnings

import click
import colorama
import yaml

from . import __version__
from sceptre import cli as sceptre_cli
from sceptre.environment import Environment
from sceptre_migration_tool import migrator


@click.group()
@click.version_option(version=__version__, prog_name="Sceptre Migration Tool")
@click.option("--debug", is_flag=True, help="Turn on debug logging.")
@click.option(
    "--dir", "directory", help="Specify sceptre_migration_tool directory.")
@click.option(
    "--var", multiple=True, help="A variable to template into config files.")
@click.option(
    "--var-file", type=click.File("rb"),
    help="A YAML file of variables to template into config files.")
@click.pass_context
def cli(
        ctx, debug, directory, var, var_file
):  # pragma: no cover
    """
    Implements sceptre_migration_tool's CLI.
    """
    setup_logging(debug)
    colorama.init()
    # Enable deprecation warnings
    warnings.simplefilter("always", DeprecationWarning)
    ctx.obj = {
        "options": {},
        "sceptre_dir": directory if directory else os.getcwd()
    }
    user_variables = {}
    if var_file:
        user_variables.update(yaml.safe_load(var_file.read()))
    if var:
        # --var options overwrite --var-file options
        for variable in var:
            variable_key, variable_value = variable.split("=")
            user_variables.update({variable_key: variable_value})
    if user_variables:
        ctx.obj["options"]["user_variables"] = user_variables


@cli.command(name="import-stack")
@sceptre_cli.stack_options
@click.argument("aws_stack_name")
@click.option("--template", "template_path", help="Specify template path.")
@click.pass_context
@sceptre_cli.catch_exceptions
def import_stack(ctx, environment, stack, aws_stack_name, template_path):
    """
    Import a Sceptre stack from AWS Cloudformation.
    """
    if not template_path:
        template_path = os.path.join(
            "templates",
            aws_stack_name + ".yaml"
        )

    migrator.import_stack(
        Environment(
            sceptre_dir=ctx.obj["sceptre_dir"],
            environment_path=environment,
            options=ctx.obj["options"]
        ),
        aws_stack_name,
        stack,
        template_path
    )


@cli.command(name="import-list")
@click.option("--list-path", "list_path", required=True,
              help="Specify the file containing the list of stacks to import. "
              "Each line in the list represents one stack and has 4 space "
              "delimited values: "
              "environment sceptre-stack-name aws-stack-name {template-path} "
              "The last is optional and if not specified by template will "
              "be assumed as templates/aws-import/{aws-stack-name}.yaml")
@click.pass_context
@sceptre_cli.catch_exceptions
def import_list(ctx, list_path):
    """
    Import a list of Sceptre stack from AWS Cloudformation.
    """
    with open(list_path, 'r') as fobj:
        migrator.import_list(ctx.obj["sceptre_dir"], ctx.obj["options"], fobj)


@cli.command(name="generate-import-list")
@click.option("--list-path", "list_path",
              help="Specify the list output file.")
@click.pass_context
@sceptre_cli.environment_options
@sceptre_cli.catch_exceptions
def generate_import_list(ctx, environment, list_path):
    """
    Generate import a list of Sceptre stack from AWS Cloudformation.
    """
    env = Environment(
        sceptre_dir=ctx.obj["sceptre_dir"],
        environment_path=environment,
        options=ctx.obj["options"]
    )

    if list_path:
        with open(list_path, 'w') as list_file_obj:
            migrator.generate_import_list(env, list_file_obj)
    else:
        migrator.generate_import_list(env)


@cli.command(name="import-env")
@sceptre_cli.environment_options
@click.pass_context
@sceptre_cli.catch_exceptions
def import_env(ctx, environment):
    """
    Import a Sceptre environment from a set of AWS CloudFormation stacks.
    """
    env = Environment(
        sceptre_dir=ctx.obj["sceptre_dir"],
        environment_path=environment,
        options=ctx.obj["options"]
    )
    migrator.import_env(env)


def setup_logging(debug):
    """
    Sets up logging.

    By default, the python logging module is configured to push logs to stdout
    as long as their level is at least INFO. The log format is set to
    "[%(asctime)s] - %(name)s - %(message)s" and the date format is set to
    "%Y-%m-%d %H:%M:%S".

    After this function has run, modules should:

    .. code:: python

        import logging

        logging.getLogger(__name__).info("my log message")

    :param debug: A flag indication whether to turn on debug logging.
    :type debug: bool
    :no_colour: A flag to indicating whether to turn off coloured output.
    :type no_colour: bool
    :returns: A logger.
    :rtype: logging.Logger
    """
    if debug:
        sceptre_logging_level = logging.DEBUG
        logging.getLogger("botocore").setLevel(logging.INFO)
    else:
        sceptre_logging_level = logging.INFO
        # Silence botocore logs
        logging.getLogger("botocore").setLevel(logging.CRITICAL)

    formatter = Formatter(
        fmt="[%(asctime)s] - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    log_handler = logging.StreamHandler()
    log_handler.setFormatter(formatter)
    logger = logging.getLogger("sceptre")
    logger.addHandler(log_handler)
    logger.setLevel(sceptre_logging_level)
    logger = logging.getLogger("sceptre_migration_tool")
    logger.addHandler(log_handler)
    logger.setLevel(sceptre_logging_level)
    return logger
