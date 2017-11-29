from behave import *
import os
import imp
import yaml
from sceptre.environment import Environment
from botocore.exceptions import ClientError


def set_template_path(context, stack_name, template_name):
    config_path = os.path.join(
        context.sceptre_dir, "config", stack_name + ".yaml"
    )
    template_path = os.path.join("templates", template_name)
    with open(config_path) as config_file:
        stack_config = yaml.safe_load(config_file)

    stack_config["template_path"] = template_path

    with open(config_path, 'w') as config_file:
        yaml.safe_dump(stack_config, config_file, default_flow_style=False)


@given('template "{template_name}" does not exist')
def step_impl(context, template_name):
    filepath = os.path.join(
        context.sceptre_dir, template_name
    )
    os.remove(filepath) if os.path.isfile(filepath) else None


@given('the template for stack "{stack_name}" is "{template_name}"')
def step_impl(context, stack_name, template_name):
    set_template_path(context, stack_name, template_name)


@given('template "{template_name}" exists')
def step_impl(context, template_name):
    filepath = os.path.join(
        context.sceptre_dir, template_name
    )
    assert os.path.exists(filepath), "template '{}' not found at '{}'".format(template_name, filepath)
    context.template_file_mtime = os.stat(filepath).st_mtime


@then('template "{template_name}" exists')
def step_impl(context, template_name):
    filepath = os.path.join(
        context.sceptre_dir, template_name
    )
    assert os.path.exists(filepath), "template '{}' not found at '{}'".format(template_name, filepath)

    
@then('template "{template_name}" is unchanged')
def step_impl(context, template_name):
    filepath = os.path.join(
        context.sceptre_dir, template_name
    )
    assert context.template_file_mtime == os.stat(filepath).st_mtime, "template '{}' has been changed.".format(template_name)

    
