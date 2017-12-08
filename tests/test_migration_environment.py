# -*- coding: utf-8 -*-

import os

from mock import sentinel, Mock, patch

from sceptre_migration_tool.reverse_resolvers import ReverseResolver
from sceptre_migration_tool.migrator import MigrationEnvironment


class TestMigrationEnvironment_import_stack_list(object):
    def test__parse_import_stack_item1(self):
        assert MigrationEnvironment._parse_import_stack_item('') is None

    def test__parse_import_stack_item2(self):
        assert MigrationEnvironment._parse_import_stack_item(' ') is None

    def test__parse_import_stack_item3(self):
        assert MigrationEnvironment._parse_import_stack_item(
            '# 1 2 3 4 '
        ) is None

    def test__parse_import_stack_item4(self):
        assert MigrationEnvironment._parse_import_stack_item(
            '1 2 3 4 '
        ) == ('1', '2', '3', '4')

    def test__parse_import_stack_item5(self):
        assert MigrationEnvironment._parse_import_stack_item(
            '1 2 3'
        ) == ('1', '2', '3', 'templates/aws-import/3.yaml')

    def test_read_import_stack_list__empty(self):
        mock_fobj = Mock()
        mock_fobj.readlines.return_value = []
        result = MigrationEnvironment.read_import_stack_list(mock_fobj)
        assert result == []

    def test_read_import_stack_list__data(self):
        mock_fobj = Mock()
        mock_fobj.readlines.return_value = ["1 2 3 4"]
        result = MigrationEnvironment.read_import_stack_list(mock_fobj)
        assert result == [('1', '2', '3', '4')]


class TestMigrationEnvironment(object):

    class MockConfig(dict):
        pass

    def setup_method(self):
        self.mock_config = self.MockConfig()
        self.mock_config['user_variables'] = {}
        self.migration_environment = MigrationEnvironment(
            connection_manager=sentinel.connection_manager,
            environment_config=self.mock_config
        )

    def test_config_correctly_initialised(self):
        assert self.migration_environment.connection_manager == \
            sentinel.connection_manager
        assert self.migration_environment.environment_config == \
            self.mock_config
        assert self.migration_environment._reversed_env_config == {}
        assert self.migration_environment._config_re_pattern == ''
        assert self.migration_environment._reverse_resolver_list is None

    @patch("sceptre_migration_tool.migration_environment.get_subclasses")
    def test__add_reverse_resolvers__no_classes(self, mock_get_subclasses):
        mock_get_subclasses.return_value = {}
        self.migration_environment._add_reverse_resolvers('fake-dir')
        mock_get_subclasses.assert_called_once_with(
            directory='fake-dir',
            class_type=ReverseResolver
        )

    @patch("sceptre_migration_tool.migration_environment.get_subclasses")
    def test__add_reverse_resolvers(self, mock_get_subclasses):
        mock_class = Mock()
        mock_get_subclasses.return_value = {'key': mock_class}
        self.migration_environment._reverse_resolver_list = []
        self.migration_environment._add_reverse_resolvers('fake-dir')
        mock_get_subclasses.assert_called_once_with(
            directory='fake-dir',
            class_type=ReverseResolver
        )
        mock_class.assert_called_once_with(
            self.migration_environment
        )

    def test_suggest__no_resolvers(self):
        self.migration_environment._reverse_resolver_list = []
        result = self.migration_environment.suggest('value')
        assert result == 'value'

    def test_suggest(self):
        def _make_reverse_resolver(return_value):
            reverse_resolver = Mock()
            reverse_resolver.suggest.return_value = return_value
            return reverse_resolver
        self.migration_environment._reverse_resolver_list = [
            _make_reverse_resolver(None),
            _make_reverse_resolver("suggest2"),
            _make_reverse_resolver("suggest3")
        ]
        result = self.migration_environment.suggest('value')
        assert result == 'suggest2'

    def test_suggest__match_env_config(self):
        self.migration_environment._reversed_env_config['value'] = \
            'fake-reversal'
        self.migration_environment._reverse_resolver_list = []
        result = self.migration_environment.suggest('value')
        assert result == 'fake-reversal'

    def test_reverse_resolver_list__pre_defined(self):
        self.migration_environment._reverse_resolver_list = 'fake-list'
        result = self.migration_environment.reverse_resolver_list
        assert 'fake-list' == result

    @patch("sceptre_migration_tool.migration_environment.MigrationEnvironment"
           "._add_reverse_resolvers")
    def test_reverse_resolver_list__search(self, mock__add_reverse_resolvers):
        self.migration_environment.environment_config.sceptre_dir = \
            'fake-sceptre-dir'
        result = self.migration_environment.reverse_resolver_list
        assert [] == result
        assert 2 == mock__add_reverse_resolvers.call_count
        mock__add_reverse_resolvers.assert_any_call(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "sceptre_migration_tool",
                "reverse_resolvers"
            )
        )
        mock__add_reverse_resolvers.assert_any_call(
            'fake-sceptre-dir/reverse_resolvers'
        )

    def test_get_internal_stack__not_found(self):
        result = \
            self.migration_environment.get_internal_stack("fake-stack-name")
        assert result is None

    def test_get_internal_stack__found(self):
        self.migration_environment.import_stack_list = [
                (
                    "fake-env-path",
                    "fake-sceptre-name",
                    "fake-stack-name",
                    "template/fake-stack-name.yaml"
                )
            ]
        result = \
            self.migration_environment.get_internal_stack("fake-stack-name")
        assert result == 'fake-env-path/fake-sceptre-name'


class TestMigrationEnvironment__reverse_env_config(object):

    class MockConfig(dict):
        pass

    def setup_method(self):
        self.mock_config = self.MockConfig()
        self.mock_config['user_variables'] = {
            'preprod_aws_profile': 'my-special-profile',
            'preprod_region': 'us-west-2',
            'preprod_vpc_id': 'vpc-abc123'
        }
        self.migration_environment = MigrationEnvironment(
            connection_manager=sentinel.connection_manager,
            environment_config=self.mock_config
        )

    def test_config_correctly_initialised(self):
        assert self.migration_environment.connection_manager == \
            sentinel.connection_manager
        assert self.migration_environment.environment_config == \
            self.mock_config
        assert self.migration_environment._reversed_env_config == {
            'my-special-profile': '{{ var.preprod_aws_profile }}',
            'us-west-2': '{{ var.preprod_region }}',
            'vpc-abc123': '{{ var.preprod_vpc_id }}'
        }
        assert self.migration_environment._config_re_pattern\
            .split('|').sort() == \
            'us\\-west\\-2|vpc\\-abc123|my\\-special\\-profile'\
            .split('|').sort()
        assert self.migration_environment._reverse_resolver_list is None

    def test__multi_subst(self):
        result = self.migration_environment._reverse_env_config(
            'my-bucket-vpc-abc123-us-west-2'
        )
        assert result ==\
            'my-bucket-{{ var.preprod_vpc_id }}-{{ var.preprod_region }}'
