# -*- coding: utf-8 -*-

from mock import patch, sentinel, Mock, PropertyMock

from sceptre.environment import Environment
from sceptre_migration_tool import migrator


class TestEnvironment(object):

    @patch("sceptre.environment.Environment._load_stacks")
    @patch(
        "sceptre.environment.Environment.is_leaf", new_callable=PropertyMock
    )
    @patch("sceptre.environment.Environment._validate_path")
    def setup_method(
            self, test_method, mock_validate_path,
            mock_is_leaf, mock_load_stacks
    ):
        mock_is_leaf.return_value = True
        mock_load_stacks.return_value = sentinel.stacks
        mock_validate_path.return_value = "environment_path"

        self.environment = Environment(
            sceptre_dir="sceptre_dir",
            environment_path="environment_path",
            options=sentinel.options
        )

        # Run the rest of the tests against a leaf environment
        self.environment._is_leaf = True

    @patch("sceptre_migration_tool.stack.import_stack")
    @patch("sceptre_migration_tool.migrator.ConnectionManager")
    @patch("sceptre.environment.Environment._get_config")
    def test_import_stack(
            self, mock_get_config, mock_ConnectionManager,
            mock_import_stack
    ):
        mock_config = {
            "region": sentinel.region,
            "iam_role": sentinel.iam_role,
            "profile": sentinel.profile
        }
        mock_get_config.return_value = mock_config
        mock_ConnectionManager.return_value = sentinel.connection_manager

        migrator.import_stack(
            self.environment,
            aws_stack_name='fake-aws-stack',
            sceptre_stack_path='fake-sceptre-stack',
            template_path='fake-template-path'
        )
        mock_ConnectionManager.assert_called_once_with(
            region=sentinel.region,
            iam_role=sentinel.iam_role,
            profile=sentinel.profile
        )

        mock_import_stack.assert_called_once_with(
            environment_config=mock_config,
            connection_manager=mock_ConnectionManager.return_value,
            aws_stack_name='fake-aws-stack',
            template_path='fake-template-path',
            config_path='environment_path/fake-sceptre-stack'
        )

    @patch("sceptre_migration_tool.stack.import_stack")
    @patch("sceptre_migration_tool.migrator.ConnectionManager")
    @patch("sceptre.environment.Environment._get_config")
    def test_import_env(
            self, mock_get_config, mock_ConnectionManager,
            mock_import_stack
    ):
        mock_config = {
            "region": sentinel.region,
            "iam_role": sentinel.iam_role,
            "profile": sentinel.profile
        }
        mock_get_config.return_value = mock_config
        mock_ConnectionManager.return_value = Mock()
        mock_ConnectionManager.return_value.call.return_value = {
            'Stacks': [
                {
                    'StackName': 'fake-aws-stack'
                }
            ]
        }

        migrator.import_env(self.environment)

        mock_ConnectionManager.assert_called_once_with(
            region=sentinel.region,
            iam_role=sentinel.iam_role,
            profile=sentinel.profile
        )

        mock_import_stack.assert_called_once_with(
            environment_config=mock_config,
            connection_manager=mock_ConnectionManager.return_value,
            aws_stack_name='fake-aws-stack',
            template_path='templates/aws-import/fake-aws-stack.yaml',
            config_path='environment_path/fake-aws-stack'
        )
