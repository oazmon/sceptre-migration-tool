
from mock import Mock

from sceptre_migration_tool.reverse_resolvers.reverse_intuit_ami\
    import ReverseIntuitAmi
from sceptre_migration_tool.migration_environment import MigrationEnvironment


class MockConfig(dict):
    pass


class TestReverseIntuitAmi(object):

    def setup_method(self, test_method):
        self.mock_connection_manager = Mock()
        self.mock_environment_config = MockConfig()
        self.mock_environment_config['user_variables'] = {}
        self.reverse_intuit_ami = ReverseIntuitAmi(
            MigrationEnvironment(
                connection_manager=self.mock_connection_manager,
                environment_config=self.mock_environment_config
            )
        )

    def test_config_correctly_initialised(self):
        assert self.reverse_intuit_ami.migration_environment\
            .connection_manager == self.mock_connection_manager
        assert self.reverse_intuit_ami.migration_environment\
            .environment_config == self.mock_environment_config
        assert self.reverse_intuit_ami.precendence() == 90

    def test_suggest(self):
        assert self.reverse_intuit_ami.suggest("value") is None
        assert self.reverse_intuit_ami.suggest("ami") is None
        assert self.reverse_intuit_ami.suggest("ami-") is None
        assert self.reverse_intuit_ami.suggest(" ami-1") is None
        assert self.reverse_intuit_ami.suggest("ami-1 ") is None
        assert self.reverse_intuit_ami.suggest("ami-1 1") is None
        assert self.reverse_intuit_ami.suggest("ami-1") == '!intuit_ami'
