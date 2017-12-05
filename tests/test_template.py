# -*- coding: utf-8 -*-

import json

import pytest
from mock import patch, Mock

from sceptre.connection_manager import ConnectionManager
from sceptre.exceptions import UnsupportedTemplateFileTypeError

from sceptre_migration_tool import template
from sceptre_migration_tool.exceptions import ImportFailureError
from sceptre_migration_tool.migration_environment import MigrationEnvironment


class TestTemplate(object):

    class MockConfig(dict):
        pass

    def setup_method(self, test_method):
        connection_manager = Mock(spec=ConnectionManager)
        environment_config = self.MockConfig()
        environment_config.sceptre_dir = 'fake-spectre-dir'
        environment_config['user_variables'] = {}
        self.reverse_resolution_service = MigrationEnvironment(
            connection_manager, environment_config)

    @patch("sceptre_migration_tool.template._write_template")
    @patch("sceptre_migration_tool.template._normalize_template_for_write")
    def test_import_template__json_template_new_json_target(
            self, mock_normalize, mock_write):
        fake_template_body = {
            'TemplateBody': {
                'Key': 'Value'
            }
        }
        fake_template_body_string = \
            json.dumps(fake_template_body['TemplateBody'])
        mock_connection_manager =\
            self.reverse_resolution_service.connection_manager
        mock_connection_manager.call.return_value = fake_template_body
        mock_normalize.return_value = fake_template_body_string

        template.import_template(
            self.reverse_resolution_service,
            'fake-aws-stack-name',
            'templates/fake-template-path.json'
        )

        mock_connection_manager.call.assert_called_once_with(
            service='cloudformation',
            command='get_template',
            kwargs={
                'StackName': 'fake-aws-stack-name',
                'TemplateStage': 'Original'
            }
        )

        mock_normalize.assert_called_once_with(
            fake_template_body['TemplateBody'],
            '.json'
        )

        mock_write.assert_called_once_with(
            'fake-spectre-dir/templates/fake-template-path.json',
            fake_template_body_string
        )

    def test__normalize_template_for_write_json_to_json(self):
        result = template._normalize_template_for_write(
            {'Key': 'Value'},
            ".json"
        )
        assert result == '{"Key": "Value"}'

    def test__normalize_template_for_write_yaml_to_json(self):
        result = template._normalize_template_for_write(
            'Key: Value\n',
            ".json"
        )
        assert result == '{"Key": "Value"}'

    def test__normalize_template_for_write_json_to_yaml(self):
        result = template._normalize_template_for_write(
            {'Key': 'Value'},
            ".yaml"
        )
        assert result == 'Key: Value\n'

    def test__normalize_template_for_write_yaml_to_yaml(self):
        result = template._normalize_template_for_write(
            'Key: Value\n',
            ".yaml"
        )
        assert result == 'Key: Value\n'

    def test__normalize_template_for_write_yaml_to_unsupported(self):
        with pytest.raises(UnsupportedTemplateFileTypeError):
            template._normalize_template_for_write('Key: Value\n', ".txt")

    @patch("sceptre_migration_tool.template.open")
    @patch("os.makedirs")
    @patch("os.path.isfile")
    def test__write_template__new_file(
            self, mock_isfile, mock_makedirs, mock_open
    ):
        mock_isfile.return_value = False

        template._write_template('fake-path/fake-file', 'fake-body')

        mock_makedirs.assert_called_once_with('fake-path')
        mock_open.called_once_with('fake-path')
        mock_open.return_value.__enter__.return_value\
            .write.called_once_with('fake-body/fake-file', 'w')

    @patch("sceptre_migration_tool.template.open")
    @patch("os.path.isfile")
    def test__write_template__existing_same_file(self, mock_isfile, mock_open):
        mock_isfile.return_value = True
        mock_open.return_value.__enter__.return_value\
            .read.return_value = 'fake-body: !Ref value'

        template._write_template('fake-path', 'fake-body: !Ref value')

        mock_open.called_once_with('fake-path', 'r')
        mock_open.return_value.read.called_once()
        mock_open.return_value.__enter__.return_value\
            .write.assert_not_called()

    @patch("sceptre_migration_tool.template.open")
    @patch("os.path.isfile")
    def test__write_template__existing_diff_file(self, mock_isfile, mock_open):
        mock_isfile.return_value = True
        mock_open.return_value.__enter__.return_value\
            .read.return_value = 'fake-diff-body'

        with pytest.raises(ImportFailureError):
            template._write_template('fake-path', 'fake-body')

        mock_open.called_once_with('fake-path')
        mock_open.return_value.read.called_once()
        mock_open.write.assert_not_called()
