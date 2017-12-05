
# from mock import Mock
from mock import sentinel
# import pytest

from sceptre_migration_tool.migration_environment import MigrationEnvironment
from sceptre_migration_tool.reverse_resolver import ReverseResolver


class MockConfig(dict):
    pass


class MockReverseResolver(ReverseResolver):
    """
    MockReverseResolver inherits from the abstract base class ReverseResolver,
    and implements the abstract methods. It is used to allow testing on
    ReverseResolver, which is not otherwise instantiable.
    """
    mock_precendence = 99
    mock_suggtestion = None

    def precendence(self):
        return self.mock_precendence

    def suggest(self, argument):
        return self.mock_suggtestion


class TestReverseResolver(object):

    class MockConfig(dict):
        pass

    def setup_method(self, test_method):
        self.reverse_exporter = MockReverseResolver(
            MigrationEnvironment(
                connection_manager=sentinel.connection_manager,
                environment_config=self.MockConfig()
            )
        )

    def test_config_correctly_initialised(self):
        assert self.reverse_exporter.migration_environment\
            .connection_manager == sentinel.connection_manager
        assert self.reverse_exporter.migration_environment\
            .environment_config == {}
        assert self.reverse_exporter.precendence() == 99
        assert self.reverse_exporter.suggest("value") is None
