# -*- coding: utf-8 -*-

"""
sceptre_migration_tool.cli

This module implements the Sceptre Migration Tool CLI
"""

import os
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
    "--output", type=click.Choice(["yaml", "json"]), default="yaml",
    help="The formatting style for command output.")
@click.option("--no-colour", is_flag=True, help="Turn off output colouring.")
@click.option(
    "--var", multiple=True, help="A variable to template into config files.")
@click.option(
    "--var-file", type=click.File("rb"),
    help="A YAML file of variables to template into config files.")
@click.pass_context
def cli(
        ctx, debug, directory, no_colour, output, var, var_file
):  # pragma: no cover
    """
    Implements sceptre_migration_tool's CLI.
    """
    sceptre_cli.setup_logging(debug, no_colour)
    colorama.init()
    # Enable deprecation warnings
    warnings.simplefilter("always", DeprecationWarning)
    ctx.obj = {
        "options": {},
        "output_format": output,
        "no_colour": no_colour,
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


@cli.command(name="import-env")
@sceptre_cli.environment_options
@click.pass_context
@sceptre_cli.catch_exceptions
def import_env(ctx, environment):
    """
    Import a Sceptre environment from a set of AWS CloudFormation stacks.
    """
    migrator.import_env(
        Environment(
            sceptre_dir=ctx.obj["sceptre_dir"],
            environment_path=environment,
            options=ctx.obj["options"]
        )
    )
