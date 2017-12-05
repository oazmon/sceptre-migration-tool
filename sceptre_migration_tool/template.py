# -*- coding: utf-8 -*-

"""
sceptre_migration_tool.importer.template

This module imports a Sceptre Template class.
"""

from six import string_types
import json
import logging
import os
import yaml

from sceptre.template import Template
from sceptre.exceptions import UnsupportedTemplateFileTypeError
from .exceptions import ImportFailureError


def import_template(reverse_resolution_service, aws_stack_name, template_path):
    """
    Saves a template imported from AWS CloudFormation.

    :param path: The absolute path to the file which stores the template.
    :type path: str
    :param body: The body of the imported template.
    :type region: str or dict
    :raises: UnsupportedTemplateFileTypeError
    """
    abs_template_path = os.path.join(
        reverse_resolution_service.environment_config.sceptre_dir,
        template_path
    )

    logging.getLogger(__name__).debug(
        "%s - Preparing to Import CloudFormation to %s",
        os.path.basename(template_path).split(".")[0],
        abs_template_path
    )

    response = reverse_resolution_service.connection_manager.call(
        service='cloudformation',
        command='get_template',
        kwargs={
            'StackName': aws_stack_name,
            'TemplateStage': 'Original'
        }
    )

    _write_template(
        abs_template_path,
        _normalize_template_for_write(
            response['TemplateBody'],
            os.path.splitext(template_path)[1]
        )
    )

    template = Template(abs_template_path, [])
    template.relative_template_path = template_path
    return template


# If body is a string it is a YAML string;
# otherwise, it is a dict resulting from JSON document.
def _normalize_template_for_write(body, ext):
    if ext == ".json":
        # if it's YAML, make it a dict
        if isinstance(body, string_types):
            body = yaml.safe_load(body)
        # now make it a JSON string
        body = json.dumps(body)

    elif ext == ".yaml":
        # if it's JSON, make it a YAML string
        if not isinstance(body, string_types):
            body = yaml.safe_dump(body, default_flow_style=False)

    else:
        raise UnsupportedTemplateFileTypeError(
                "Template file has has extension {}. Only .yaml, "
                "and .json are supported, when importing from AWS.".format(ext)
        )
    return body


def _write_template(path, body):
    if not os.path.isfile(path):
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, 'w') as template_file:
            template_file.write(body)
    else:
        with open(path, 'r') as template_file:
            existing_body = template_file.read()

        def default_ctor(loader, tag_suffix, node):
            return tag_suffix + ' ' + str(node.value)

        yaml.add_multi_constructor('', default_ctor)
        if yaml.load(existing_body) != yaml.load(body):
            raise ImportFailureError(
                "Unable to import template. "
                "File already exists and is different: "
                "file = {}, existing_body={}, new_body={}"
                .format(path, existing_body, body)
            )
