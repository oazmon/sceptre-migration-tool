# -*- coding: utf-8 -*-

from mock import patch, sentinel, Mock, PropertyMock

from sceptre.environment import Environment

from sceptre_migration_tool import migrator


class TestMigrator(object):

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
    @patch("sceptre_migration_tool.migrator"
           "._create_reverse_resolution_service")
    def test_import_stack(
            self, mock_reverse_resolution_service,
            mock_import_stack
    ):
        migrator.import_stack(
            self.environment,
            aws_stack_name='fake-aws-stack',
            sceptre_stack_path='fake-sceptre-stack',
            template_path='fake-template-path'
        )

        mock_import_stack.assert_called_once_with(
            reverse_resolution_service=mock_reverse_resolution_service
            .return_value,
            aws_stack_name='fake-aws-stack',
            template_path='fake-template-path',
            config_path='environment_path/fake-sceptre-stack'
        )

    @patch("sceptre_migration_tool.stack.import_stack")
    @patch("sceptre_migration_tool.migrator"
           "._create_reverse_resolution_service")
    def test_import_env(
            self, mock_reverse_resolution_service,
            mock_import_stack
    ):
        mock_connection_manager =\
            mock_reverse_resolution_service.return_value.connection_manager
        mock_connection_manager.call.side_effect = [
            {
                'Stacks': [
                    {
                        'StackName': 'fake-aws-stack1'
                    }
                ],
                'NextToken': 'StackName2'
            },
            {
                'Stacks': [
                    {
                        'StackName': 'fake-aws-stack2'
                    }
                ]
            }
        ]

        migrator.import_env(self.environment)

        assert 2 == mock_import_stack.call_count

        mock_import_stack.assert_any_call(
            reverse_resolution_service=mock_reverse_resolution_service
            .return_value,
            aws_stack_name='fake-aws-stack1',
            config_path='environment_path/fake-aws-stack1',
            template_path='templates/aws-import/fake-aws-stack1.yaml'
        )

        mock_import_stack.assert_any_call(
            reverse_resolution_service=mock_reverse_resolution_service
            .return_value,
            aws_stack_name='fake-aws-stack2',
            config_path='environment_path/fake-aws-stack2',
            template_path='templates/aws-import/fake-aws-stack2.yaml'
        )


class TestEnvironment__create_reverse_resolution_service(object):

    @patch("sceptre_migration_tool.migrator.ConnectionManager")
    def test_happy_case(self, mock_ConnectionManager):
        mock_env = Mock()
        mock_env._get_config.return_value = {
            "region": 'fake-region',
            "iam_role": 'fake-iam-role',
            "profile": 'fake-profile'
        }

        result = migrator._create_reverse_resolution_service(mock_env)

        assert result.connection_manager == mock_ConnectionManager.return_value
        assert result.environment_config == mock_env._get_config()

        mock_ConnectionManager.assert_called_once_with(
            region='fake-region',
            iam_role='fake-iam-role',
            profile='fake-profile'
        )
