# -*- coding: utf-8 -*-

# import pytest
from mock import patch, Mock

from sceptre_migration_tool import stack


class TestStack(object):

    @patch("sceptre_migration_tool.stack.Stack")
    @patch("sceptre_migration_tool.stack.import_config")
    @patch("sceptre_migration_tool.stack.import_template")
    def test_import_stack(self, mock_template, mock_config, mock_stack):
        mock_environment_config = Mock()
        mock_environment_config.sceptre_dir = \
            'fake-sceptre_migration_tool-dir'
        mock_template.return_value = Mock()
        mock_connection_manager = Mock()
        mock_connection_manager.call.return_value = {
            'TemplateBody': 'fake-body'
        }

        result = stack.import_stack(
            mock_environment_config,
            mock_connection_manager,
            'fake-aws-stack-name',
            'fake-template-path.yaml',
            'fake-config-path'
        )
        assert result is not None

        mock_template.assert_called_once_with(
            mock_connection_manager,
            'fake-aws-stack-name',
            'fake-sceptre_migration_tool-dir/fake-template-path.yaml'
        )

        mock_config.assert_called_once_with(
            mock_template.return_value,
            mock_connection_manager,
            'fake-aws-stack-name',
            'fake-sceptre_migration_tool-dir/config/fake-config-path'
        )

        mock_stack.assert_called_once_with(
            connection_manager=mock_connection_manager,
            environment_config=mock_environment_config,
            name='fake-config-path'
        )
