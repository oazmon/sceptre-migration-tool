# -*- coding: utf-8 -*-

# import pytest
from mock import patch, Mock

from sceptre.connection_manager import ConnectionManager

from sceptre_migration_tool import stack
from sceptre_migration_tool.migration_environment import MigrationEnvironment


class TestStack(object):

    class MockConfig(dict):
        pass

    def setup_method(self, test_method):
        connection_manager = Mock(spec=ConnectionManager)
        environment_config = self.MockConfig()
        environment_config['sceptre_dir'] = 'fake-spectre-dir'
        environment_config['user_variables'] = {}
        self.migration_environment = MigrationEnvironment(
            connection_manager, environment_config)

    @patch("sceptre_migration_tool.stack.Stack")
    @patch("sceptre_migration_tool.stack.import_config")
    @patch("sceptre_migration_tool.stack.import_template")
    def test_import_stack(self, mock_template, mock_config, mock_stack):
        mock_template.return_value = Mock()
        mock_connection_manager =\
            self.migration_environment.connection_manager
        mock_environment_config =\
            self.migration_environment.environment_config
        mock_connection_manager.call.return_value = {
            'TemplateBody': 'fake-body'
        }

        result = stack.import_stack(
            self.migration_environment,
            'fake-aws-stack-name',
            'fake-template-path.yaml',
            'fake-config-path'
        )
        assert result is not None

        mock_template.assert_called_once_with(
            self.migration_environment,
            'fake-aws-stack-name',
            'fake-template-path.yaml'
        )

        mock_config.assert_called_once_with(
            self.migration_environment,
            'fake-aws-stack-name',
            'fake-config-path',
            mock_template.return_value
        )

        mock_stack.assert_called_once_with(
            connection_manager=mock_connection_manager,
            environment_config=mock_environment_config,
            name='fake-config-path'
        )
