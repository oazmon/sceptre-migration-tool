
from mock import Mock, patch

from sceptre_migration_tool.reverse_resolver.reverse_stack_output\
    import ReverseStackOutput
from sceptre_migration_tool.migration_environment import MigrationEnvironment


class MockConfig(dict):
    pass


class TestReverseStackOutput(object):

    def setup_method(self, test_method):
        self.mock_connection_manager = Mock()
        self.reverse_stack_output = ReverseStackOutput(
            MigrationEnvironment(
                connection_manager=self.mock_connection_manager,
                environment_config=MockConfig()
            )
        )

    def test_config_correctly_initialised(self):
        assert self.reverse_stack_output.migration_environment\
            .connection_manager == self.mock_connection_manager
        assert self.reverse_stack_output.migration_environment\
            .environment_config == {}
        assert self.reverse_stack_output.precendence() == 20

    def test__add_to_reverse_lookup__has_export(self):
        reverse_lookup = {}
        self.reverse_stack_output._add_to_reverse_lookup(
            stack_name='fake-stack-name',
            output={
                'ExportName': 'fake-export',
                'OutputKey': 'fake-key1',
                'OutputValue': 'value1'
            },
            target_dict=reverse_lookup,
            resolver_name='fake-resolver'
        )
        assert {} == reverse_lookup

    def test__add_to_reverse_lookup__good(self):
        reverse_lookup = {}
        self.reverse_stack_output._add_to_reverse_lookup(
            stack_name='fake-stack-name',
            output={
                'OutputKey': 'fake-key1',
                'OutputValue': 'value1'
            },
            target_dict=reverse_lookup,
            resolver_name='fake-resolver'
        )
        assert reverse_lookup == {
                'value1': '!fake-resolver fake-stack-name::fake-key1'
            }

    def test__add_to_reverse_lookup__dup(self):
        reverse_lookup = {'value1': 'fake-older-value'}
        self.reverse_stack_output._add_to_reverse_lookup(
            stack_name='fake-stack-name',
            output={
                'OutputKey': 'fake-key1',
                'OutputValue': 'value1'
            },
            target_dict=reverse_lookup,
            resolver_name='fake-resolver'
        )
        assert reverse_lookup == {'value1': 'fake-older-value'}

    @patch("sceptre_migration_tool.reverse_resolver.reverse_stack_output."
           "ReverseStackOutput._add_to_reverse_lookup")
    def test__build_external_stack_lookup(
            self, mock_add_one
    ):
        self.reverse_stack_output._stack_output_external = {}
        self.reverse_stack_output._build_external_stack_lookup(
            stack_name='fake-stack-name',
            outputs=[
                {
                    'OutputKey': 'fake-key1',
                    'OutputValue': 'value1'
                },
                {
                    'OutputKey': 'fake-key2',
                    'OutputValue': 'value2'
                }
            ]
        )
        assert 2 == mock_add_one.call_count
        mock_add_one.assert_any_call(
            stack_name='fake-stack-name',
            output={
                    'OutputKey': 'fake-key1',
                    'OutputValue': 'value1'
            },
            target_dict=self.reverse_stack_output._stack_output_external,
            resolver_name="stack_output_external"
        )
        mock_add_one.assert_any_call(
            stack_name='fake-stack-name',
            output={
                    'OutputKey': 'fake-key2',
                    'OutputValue': 'value2'
            },
            target_dict=self.reverse_stack_output._stack_output_external,
            resolver_name="stack_output_external"
        )

    @patch("sceptre_migration_tool.reverse_resolver.reverse_stack_output."
           "ReverseStackOutput._add_to_reverse_lookup")
    def test__build_internal_stack_lookup(
            self, mock_add_one
    ):
        self.reverse_stack_output._stack_output = {}
        self.reverse_stack_output._build_internal_stack_lookup(
            stack_name='fake-stack-name',
            outputs=[
                {
                    'OutputKey': 'fake-key1',
                    'OutputValue': 'value1'
                },
                {
                    'OutputKey': 'fake-key2',
                    'OutputValue': 'value2'
                }
            ]
        )
        assert 2 == mock_add_one.call_count
        mock_add_one.assert_any_call(
            stack_name='fake-stack-name',
            output={
                    'OutputKey': 'fake-key1',
                    'OutputValue': 'value1'
            },
            target_dict=self.reverse_stack_output._stack_output,
            resolver_name="stack_output"
        )
        mock_add_one.assert_any_call(
            stack_name='fake-stack-name',
            output={
                    'OutputKey': 'fake-key2',
                    'OutputValue': 'value2'
            },
            target_dict=self.reverse_stack_output._stack_output,
            resolver_name="stack_output"
        )

    @patch("sceptre_migration_tool.reverse_resolver.reverse_stack_output."
           "ReverseStackOutput._build_external_stack_lookup")
    @patch("sceptre_migration_tool.reverse_resolver.reverse_stack_output."
           "ReverseStackOutput._build_internal_stack_lookup")
    def test__build_reverse_lookup__no_outputs(
            self, mock_build_internal, mock_build_external
    ):
        self.reverse_stack_output._build_reverse_lookup({})
        mock_build_internal.assert_not_called()
        mock_build_external.assert_not_called()

    @patch("sceptre_migration_tool.reverse_resolver.reverse_stack_output."
           "ReverseStackOutput._build_external_stack_lookup")
    @patch("sceptre_migration_tool.reverse_resolver.reverse_stack_output."
           "ReverseStackOutput._build_internal_stack_lookup")
    def test__build_reverse_lookup__internal_stack(
            self, mock_build_internal, mock_build_external
    ):
        mock_get_internal_stack = Mock()
        mock_get_internal_stack.return_value = 'fake-internal-stack-name'
        self.reverse_stack_output.migration_environment.get_internal_stack =\
            mock_get_internal_stack
        stack = {
            'StackName': 'fake-stack-name',
            'Outputs': [
                {
                    'OutputKey': 'fake-key1',
                    'OutputValue': 'value1'
                },
                {
                    'OutputKey': 'fake-key2',
                    'OutputValue': 'value2'
                }
            ]
        }
        self.reverse_stack_output._build_reverse_lookup(stack)
        mock_build_internal.assert_called_once_with(
            'fake-internal-stack-name',
            stack['Outputs']
        )
        mock_build_external.assert_not_called()

    @patch("sceptre_migration_tool.reverse_resolver.reverse_stack_output."
           "ReverseStackOutput._build_external_stack_lookup")
    @patch("sceptre_migration_tool.reverse_resolver.reverse_stack_output."
           "ReverseStackOutput._build_internal_stack_lookup")
    def test__build_reverse_lookup__external_stack(
            self, mock_build_internal, mock_build_external
    ):
        mock_get_internal_stack = Mock()
        mock_get_internal_stack.return_value = None
        self.reverse_stack_output.migration_environment.get_internal_stack =\
            mock_get_internal_stack
        stack = {
            'StackName': 'fake-stack-name',
            'Outputs': [
                {
                    'OutputKey': 'fake-key1',
                    'OutputValue': 'value1'
                },
                {
                    'OutputKey': 'fake-key2',
                    'OutputValue': 'value2'
                }
            ]
        }
        self.reverse_stack_output._build_reverse_lookup(stack)
        mock_build_internal.assert_not_called()
        mock_build_external.assert_called_once_with(
            stack['StackName'],
            stack['Outputs']
        )

    def test__get_stack_output__no_stacks(self):
        self.mock_connection_manager.call.return_value = {
            'StackSummaries': []
        }
        self.reverse_stack_output._get_stack_output()
        assert {} == self.reverse_stack_output._stack_output
        assert {} == self.reverse_stack_output._stack_output_external

    @patch("sceptre_migration_tool.reverse_resolver.reverse_stack_output."
           "ReverseStackOutput._build_reverse_lookup")
    def test__get_stack_output__good(self, mock_build_reverse_lookup):
        self.mock_stack1 = Mock()
        self.mock_stack2 = Mock()
        self.mock_stack3 = Mock()
        self.mock_connection_manager.call.side_effect = [
            {
                'StackSummaries': [
                    self.mock_stack1,
                    self.mock_stack2
                ],
                'NextToken': 'fake-next-token'
            },
            {
                'StackSummaries': [
                    self.mock_stack3
                ]
            }
        ]
        self.reverse_stack_output._get_stack_output()
        assert mock_build_reverse_lookup.call_count == 3
        mock_build_reverse_lookup.assert_any_call(self.mock_stack1)
        mock_build_reverse_lookup.assert_any_call(self.mock_stack2)
        mock_build_reverse_lookup.assert_any_call(self.mock_stack3)

    @patch("sceptre_migration_tool.reverse_resolver.reverse_stack_output."
           "ReverseStackOutput._get_stack_output")
    def test_suggest__not_found(self, mock_get_stack_output):
        def _get_stack_output_side_effect():
            self.reverse_stack_output._stack_output = {}
            self.reverse_stack_output._stack_output_external = {}
        mock_get_stack_output.side_effect = _get_stack_output_side_effect

        assert self.reverse_stack_output.suggest('fake-value') is None

        mock_get_stack_output.assert_called_once()

    @patch("sceptre_migration_tool.reverse_resolver.reverse_stack_output."
           "ReverseStackOutput._get_stack_output")
    def test_suggest__is_internal(self, mock_get_stack_output):
        def _get_stack_output_side_effect():
            self.reverse_stack_output._stack_output = {
                'fake-value': 'fake-internal-key'
            }
            self.reverse_stack_output._stack_output_external = {}
        mock_get_stack_output.side_effect = _get_stack_output_side_effect

        assert self.reverse_stack_output.suggest('fake-value') ==\
            'fake-internal-key'

        mock_get_stack_output.assert_called_once()

    @patch("sceptre_migration_tool.reverse_resolver.reverse_stack_output."
           "ReverseStackOutput._get_stack_output")
    def test_suggest__is_external(self, mock_get_stack_output):
        def _get_stack_output_side_effect():
            self.reverse_stack_output._stack_output = {}
            self.reverse_stack_output._stack_output_external = {
                'fake-value': 'fake-external-key'
            }
        mock_get_stack_output.side_effect = _get_stack_output_side_effect

        assert self.reverse_stack_output.suggest('fake-value') ==\
            'fake-external-key'

        mock_get_stack_output.assert_called_once()
