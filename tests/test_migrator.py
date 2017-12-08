# -*- coding: utf-8 -*-

from StringIO import StringIO
from mock import patch, sentinel, Mock, PropertyMock

from sceptre.environment import Environment

from sceptre_migration_tool.migration_environment import MigrationEnvironment
from sceptre_migration_tool import migrator


class TestMigrator_ensure_env_dir_exists(object):
    @patch("sceptre_migration_tool.cli.os.makedirs")
    @patch("sceptre_migration_tool.cli.os.path.isdir")
    def test_is_dir(self, mock_isdir, mock_makedirs):
        mock_isdir.return_value = True
        migrator._ensure_env_dir_exists("sceptre_dir", "environment\\path")
        mock_isdir.assert_called_once_with("sceptre_dir/environment/path")
        mock_makedirs.assert_not_called()

    @patch("sceptre_migration_tool.cli.os.makedirs")
    @patch("sceptre_migration_tool.cli.os.path.isdir")
    def test_is_NOT_dir(self, mock_isdir, mock_makedirs):
        mock_isdir.return_value = False
        migrator._ensure_env_dir_exists("sceptre_dir", "environment\\path")
        mock_isdir.assert_called_once_with("sceptre_dir/environment/path")
        mock_makedirs.assert_called_once_with("sceptre_dir/environment/path")


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
           "._create_migration_environment")
    def test_import_stack(
            self, mock_migration_environment,
            mock_import_stack
    ):
        migrator.import_stack(
            self.environment,
            aws_stack_name='fake-aws-stack',
            sceptre_stack_path='fake-sceptre-stack',
            template_path='fake-template-path'
        )

        mock_import_stack.assert_called_once_with(
            migration_environment=mock_migration_environment.return_value,
            aws_stack_name='fake-aws-stack',
            template_path='fake-template-path',
            config_path='environment_path/fake-sceptre-stack'
        )

    @patch("sceptre_migration_tool.stack.import_stack")
    @patch("sceptre_migration_tool.migrator"
           "._create_migration_environment")
    def test_import_env(
            self, mock_migration_environment,
            mock_import_stack
    ):
        mock_connection_manager =\
            mock_migration_environment.return_value.connection_manager
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
            migration_environment=mock_migration_environment
            .return_value,
            aws_stack_name='fake-aws-stack1',
            config_path='environment_path/fake-aws-stack1',
            template_path='templates/aws-import/fake-aws-stack1.yaml'
        )

        mock_import_stack.assert_any_call(
            migration_environment=mock_migration_environment
            .return_value,
            aws_stack_name='fake-aws-stack2',
            config_path='environment_path/fake-aws-stack2',
            template_path='templates/aws-import/fake-aws-stack2.yaml'
        )

    @patch("sceptre_migration_tool.migrator.import_stack")
    @patch("sceptre_migration_tool.migrator.Environment")
    @patch("sceptre_migration_tool.migration_environment"
           ".MigrationEnvironment.read_import_stack_list")
    def test_import_list__empty_list(
            self, mock_read_import_stack_list,
            mock_environment,
            mock_import_stack
    ):
        mock_read_import_stack_list.return_value = []
        migrator.import_list(
            "sceptre_dir", sentinel.options, sentinel.list_fobj
        )
        mock_read_import_stack_list.assert_called_once_with(sentinel.list_fobj)
        mock_environment.assert_not_called()
        mock_import_stack.assert_not_called()

    @patch("sceptre_migration_tool.migrator.import_stack")
    @patch("sceptre_migration_tool.migrator.Environment")
    @patch("sceptre_migration_tool.migration_environment"
           ".MigrationEnvironment.read_import_stack_list")
    def test_import_list__data(
            self, mock_read_import_stack_list,
            mock_environment,
            mock_import_stack
    ):
        fake_item = ('1', '2', '3', '4')
        mock_read_import_stack_list.return_value = [fake_item]
        migrator.import_list(
            "sceptre_dir", sentinel.options, sentinel.list_fobj
        )
        mock_read_import_stack_list.assert_called_once_with(sentinel.list_fobj)
        mock_environment.assert_called_once_with(
            sceptre_dir="sceptre_dir",
            environment_path=fake_item[MigrationEnvironment.PART_ENV],
            options=sentinel.options
        )
        mock_import_stack.assert_called_once_with(
            mock_environment.return_value,
            fake_item[MigrationEnvironment.PART_AWS_STACK_NAME],
            fake_item[MigrationEnvironment.PART_SCEPTRE_STACK_NAME],
            fake_item[MigrationEnvironment.PART_TEMPLATE_PATH]
        )

    @patch("sceptre_migration_tool.migrator"
           "._create_migration_environment")
    def test_generate_import_list__empty(
            self, mock_migration_environment
    ):
        mock_connection_manager =\
            mock_migration_environment.return_value.connection_manager
        mock_connection_manager.call.return_value = {
            'Stacks': []
        }
        try:
            list_fobj = StringIO()
            migrator.generate_import_list(
                self.environment, list_fobj
            )
            assert "" == list_fobj.getvalue()
        finally:
            list_fobj.close()
        mock_connection_manager.call.assert_called_once_with(
            service='cloudformation',
            command='describe_stacks',
            kwargs={}
        )

    @patch("sceptre_migration_tool.migrator"
           "._create_migration_environment")
    def test_generate_import_list__data(
            self, mock_migration_environment
    ):
        mock_connection_manager =\
            mock_migration_environment.return_value.connection_manager
        mock_connection_manager.call.side_effect = [
            {
                'Stacks': [
                    {
                        'StackName': 'name1'
                    },
                    {
                        'StackName': 'name2'
                    }
                ],
                'NextToken': 'next'
            },
            {
                'Stacks': [
                    {
                        'StackName': 'name3'
                    }
                ]
            }
        ]
        try:
            list_fobj = StringIO()
            migrator.generate_import_list(
                self.environment, list_fobj
            )
            assert list_fobj.getvalue() == '\n'.join([
                'environment_path name1 name1 templates/aws-import/name1.yaml',
                'environment_path name2 name2 templates/aws-import/name2.yaml',
                'environment_path name3 name3 templates/aws-import/name3.yaml',
                ''
            ])
        finally:
            list_fobj.close()
        mock_connection_manager.call.call_count = 2


class TestEnvironment__create_migration_environment(object):

    @patch("sceptre_migration_tool.migrator.ConnectionManager")
    def test_happy_case(self, mock_ConnectionManager):
        mock_env = Mock()
        mock_env._get_config.return_value = {
            "region": 'fake-region',
            "iam_role": 'fake-iam-role',
            "profile": 'fake-profile',
            "user_variables": {}
        }

        result = migrator._create_migration_environment(mock_env)

        assert result.connection_manager == mock_ConnectionManager.return_value
        assert result.environment_config == mock_env._get_config()

        mock_ConnectionManager.assert_called_once_with(
            region='fake-region',
            iam_role='fake-iam-role',
            profile='fake-profile'
        )
