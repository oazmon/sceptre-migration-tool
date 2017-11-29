# -*- coding: utf-8 -*-

from contextlib import contextmanager
from tempfile import mkdtemp
import shutil
import json
from mock import patch, Mock, call
import pytest

from sceptre_migration_tool import config
from sceptre_migration_tool.exceptions import ImportFailureError
from sceptre.template import Template


class TestConfig(object):

    @contextmanager
    def _create_temp_dir(self):
        temp_directory = mkdtemp()
        yield temp_directory
        shutil.rmtree(temp_directory)

    @patch("sceptre_migration_tool.config.os.path.isfile")
    def test_import_config__exists(
        self, mock_isfile
    ):
        mock_connection_manager = Mock()
        mock_isfile.return_value = True
        with pytest.raises(ImportFailureError):
            config.import_config(
                template=Template('fake-path', []),
                connection_manager=mock_connection_manager,
                aws_stack_name="fake-aws-stack-name",
                config_path="environment-path/config"
            )

    @patch("sceptre_migration_tool.config.print")
    @patch("sceptre_migration_tool.config.open")
    @patch("sceptre_migration_tool.config.os.path.isfile")
    def test_import_config__empty_stack(
        self, mock_isfile, mock_open, mock_print
    ):
        mock_connection_manager = Mock()
        mock_connection_manager.call.return_value = {'Stacks': [
                {
                }
            ]}

        mock_isfile.return_value = False
        fake_template = Template('fake-path', [])
        fake_template.relative_template_path = 'fake-relative-path'
        config.import_config(
            template=fake_template,
            connection_manager=mock_connection_manager,
            aws_stack_name="fake-aws-stack-name",
            config_path="environment-path/fake-stack"
        )

        mock_open.assert_called_with(
            "environment-path/fake-stack.yaml",
            'w'
        )

        mock_print.assert_has_calls(
            [
                call(
                    "template_path: fake-relative-path",
                    file=mock_open.return_value.__enter__.return_value
                ),
                call(
                    "stack_name: fake-aws-stack-name",
                    file=mock_open.return_value.__enter__.return_value
                )
            ],
            any_order=False
        )

    @patch("sceptre_migration_tool.config.print")
    @patch("sceptre_migration_tool.config.open")
    @patch("sceptre_migration_tool.config.os.path.isfile")
    def test_import_config__all_details_stack(
        self, mock_isfile, mock_open, mock_print
    ):
        mock_template = Mock()
        mock_template.path = 'fake-path'
        mock_template.relative_template_path = 'fake-relative-path.yaml'
        mock_template.body = json.dumps({
            'Parameters': {
                'fake-key1': {
                },
                'fake-key2': {
                    'Default': 'wrong-value'
                },
                'fake-key3': {
                    'Default': 'match-default-value'
                }
            }
        })
        mock_connection_manager = Mock()
        mock_connection_manager.call.return_value = {'Stacks': [
                {
                    'EnableTerminationProtection': True,
                    'RoleARN': 'fake-role-arn',
                    'Parameters': [
                        {
                            'ParameterKey': 'fake-key1',
                            'ParameterValue': 'no-default-value'
                        },
                        {
                            'ParameterKey': 'fake-key2',
                            'ParameterValue': 'mismatch-default-value'
                        },
                        {
                            'ParameterKey': 'fake-key3',
                            'ParameterValue': 'match-default-value'
                        }
                    ],
                    'Tags': [
                        {
                            'Key': 'fake-tag-key',
                            'Value': 'fake-tag-value'
                        }
                    ]
                }
            ]}

        mock_isfile.return_value = False
        config.import_config(
            template=mock_template,
            connection_manager=mock_connection_manager,
            aws_stack_name="fake-aws-stack-name",
            config_path="environment-path/fake-stack"
        )

        expected_calls = [
            call(
                "template_path: fake-relative-path.yaml",
                file=mock_open.return_value.__enter__.return_value
            ),
            call(
                "stack_name: fake-aws-stack-name",
                file=mock_open.return_value.__enter__.return_value
            ),
            call(
                "protect: True",
                file=mock_open.return_value.__enter__.return_value
            ),
            call(
                "role_arn: fake-role-arn",
                file=mock_open.return_value.__enter__.return_value
            ),
            call(
                "parameters:",
                file=mock_open.return_value.__enter__.return_value
            ),
            call(
                "  fake-key1: no-default-value",
                file=mock_open.return_value.__enter__.return_value
            ),
            call(
                "  fake-key2: mismatch-default-value",
                file=mock_open.return_value.__enter__.return_value
            ),
            call(
                "  #fake-key3: match-default-value",
                file=mock_open.return_value.__enter__.return_value
            ),
            call(
                "stack_tags:",
                file=mock_open.return_value.__enter__.return_value
            ),
            call(
                "  fake-tag-key: fake-tag-value",
                file=mock_open.return_value.__enter__.return_value
            )
        ]
        mock_print.assert_has_calls(
            expected_calls,
            any_order=False
        )
