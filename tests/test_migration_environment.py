# -*- coding: utf-8 -*-

import os

from mock import sentinel, Mock, patch

from sceptre_migration_tool.reverse_resolver import ReverseResolver
from sceptre_migration_tool.migrator import MigrationEnvironment


class TestMigrationEnvironment(object):

    class MockConfig(dict):
        pass

    def setup_method(self):
        self.mock_config = self.MockConfig()
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

    def test_reverse_resolver__no_resolvers(self):
        self.migration_environment._reverse_resolver_list = []
        result = self.migration_environment.reverse_resolve('value')
        assert result == 'value'

    def test_reverse_resolver(self):
        def _make_reverse_resolver(return_value):
            reverse_resolver = Mock()
            reverse_resolver.suggest.return_value = return_value
            return reverse_resolver
        self.migration_environment._reverse_resolver_list = [
            _make_reverse_resolver(None),
            _make_reverse_resolver("suggest2"),
            _make_reverse_resolver("suggest3")
        ]
        result = self.migration_environment.reverse_resolve('value')
        assert result == 'suggest2'

    def test_reverse_resolver_list__pre_defined(self):
        self.migration_environment._reverse_resolver_list = 'fake-list'
        result = self.migration_environment.reverse_resolver_list
        assert 'fake-list' == result

    @patch("sceptre_migration_tool.migration_environment.MigrationEnvironment"
           "._add_reverse_resolvers")
    def test_reverse_resolver_list__search(self, mock__add_reverse_resolvers):
        self.migration_environment.environment_config['sceptre_dir'] = \
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


class TestMigrationEnvironment__reverse_env_config(object):

    class MockConfig(dict):
        pass

    def setup_method(self):
        self.mock_config = self.MockConfig()
        self.mock_config['preprod_aws_profile'] = 'my-special-profile'
        self.mock_config['preprod_region'] = 'us-west-2'
        self.mock_config['preprod_vpc_id'] = 'vpc-abc123'
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
            'my-special-profile': '{{ preprod_aws_profile }}',
            'us-west-2': '{{ preprod_region }}',
            'vpc-abc123': '{{ preprod_vpc_id }}'
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
        assert 'my-bucket-{{ preprod_vpc_id }}-{{ preprod_region }}' == result
