
from mock import Mock, patch, sentinel
# import pytest

from sceptre_migration_tool.reverse_resolver.reverse_exports\
    import ReverseExports


class TestReverseResolver(object):

    def setup_method(self, test_method):
        self.reverse_resolver = ReverseExports(
            connection_manager=sentinel.connection_manager,
            environment_config=sentinel.environment_config
        )

    def test_config_correctly_initialised(self):
        assert self.reverse_resolver.connection_manager == \
            sentinel.connection_manager
        assert self.reverse_resolver.environment_config == \
            sentinel.environment_config
        assert self.reverse_resolver.precendence() == 10

    @patch("sceptre_migration_tool.reverse_resolver.reverse_exports."
           "ReverseExports._get_exports")
    def test_suggest__no_suggestions(self, mock_get_exports):
        mock_get_exports.return_value = {}
        assert self.reverse_resolver.suggest("value") is None
        mock_get_exports.assert_called_once()

    @patch("sceptre_migration_tool.reverse_resolver.reverse_exports."
           "ReverseExports._get_exports")
    def test_suggest__has_suggestions(self, mock_get_exports):
        mock_get_exports.return_value = {'value': '!stack_export key'}
        assert self.reverse_resolver.suggest("value") == '!stack_export key'
        mock_get_exports.assert_called_once()

    def test__get_exports__none_found(self):
        self.reverse_resolver.connection_manager = Mock()
        self.reverse_resolver.connection_manager.call.return_value = {
            'Exports': []
        }
        result = self.reverse_resolver._get_exports()
        assert result == {}
        self.reverse_resolver.connection_manager.call.assert_called_once_with(
                service="cloudformation",
                command="list_exports",
                kwargs={}
        )

    def test__get_exports__some_found(self):
        self.reverse_resolver.connection_manager = Mock()
        self.reverse_resolver.connection_manager.call.side_effect = [
            {
                'Exports': [
                    {
                        'Name': 'fake-key1',
                        'Value': 'fake-value1'
                    }
                ],
                'NextToken': 'fake-next'
            },
            {
                'Exports': [
                    {
                        'Name': 'fake-key2',
                        'Value': 'fake-value2'
                    },
                    {
                        'Name': 'fake-dup-key1',
                        'Value': 'fake-value1'
                    }
                ]
            }
        ]
        result = self.reverse_resolver._get_exports()
        assert result == {
            'fake-value1': '!stack_export fake-key1',
            'fake-value2': '!stack_export fake-key2'
        }
        assert 2 == self.reverse_resolver.connection_manager.call.call_count
        self.reverse_resolver.connection_manager.call.assert_any_call(
                service="cloudformation",
                command="list_exports",
                kwargs={}
        )
        self.reverse_resolver.connection_manager.call.assert_any_call(
                service="cloudformation",
                command="list_exports",
                kwargs={'NextToken': 'fake-next'}
        )
