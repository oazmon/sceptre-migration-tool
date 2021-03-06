
import logging
import os

from click.testing import CliRunner
from mock import patch, sentinel

from sceptre_migration_tool import cli


class TestCli(object):

    def setup_method(self, test_method):
        self.runner = CliRunner()

    def test_setup_logging_with_debug(self):
        logger = cli.setup_logging(True)
        assert logger.getEffectiveLevel() == logging.DEBUG
        assert logging.getLogger("botocore").getEffectiveLevel() == \
            logging.INFO

        # Silence logging for the rest of the tests
        logger.setLevel(logging.CRITICAL)

    def test_setup_logging_without_debug(self):
        logger = cli.setup_logging(False)
        assert logger.getEffectiveLevel() == logging.INFO
        assert logging.getLogger("botocore").getEffectiveLevel() == \
            logging.CRITICAL

        # Silence logging for the rest of the tests
        logger.setLevel(logging.CRITICAL)

    @patch("sceptre_migration_tool.migrator.import_stack")
    @patch("sceptre_migration_tool.cli.os.getcwd")
    @patch("sceptre_migration_tool.cli.Environment")
    def test_import_stack_default_template_dir(
            self, mock_env, mock_getcwd, mock_import_stack
    ):
        mock_getcwd.return_value = sentinel.cwd
        result = self.runner.invoke(
            cli.cli,
            ["import-stack", "dev", "vpc", "fake-aws-stack"]
        )
        assert result.exit_code == 0
        mock_env.assert_called_with(
            sceptre_dir=sentinel.cwd,
            environment_path=u'dev',
            options={}
        )
        fake_template_path = os.path.join(
            "templates",
            "fake-aws-stack.yaml"
        )

        mock_import_stack.assert_called_with(
            mock_env.return_value,
            "fake-aws-stack",
            "vpc",
            fake_template_path
        )

    @patch("sceptre_migration_tool.migrator.import_stack")
    @patch("sceptre_migration_tool.cli.os.getcwd")
    @patch("sceptre_migration_tool.cli.Environment")
    def test_import_stack_user_template_dir(
            self, mock_env, mock_getcwd, mock_import_stack
    ):
        mock_getcwd.return_value = sentinel.cwd
        fake_template_path = "user-templates/fake-aws-stack.yaml"
        result = self.runner.invoke(cli.cli, [
                "import-stack",
                "--template", fake_template_path,
                "dev",
                "vpc",
                "fake-aws-stack"
            ]
        )
        assert 0 == result.exit_code
        mock_env.assert_called_with(
            sceptre_dir=sentinel.cwd,
            environment_path=u'dev',
            options={}
        )
        mock_import_stack.assert_called_with(
            mock_env.return_value,
            "fake-aws-stack",
            "vpc",
            fake_template_path
        )

    @patch("sceptre_migration_tool.migrator.import_env")
    @patch("sceptre_migration_tool.cli.os.getcwd")
    @patch("sceptre_migration_tool.cli.Environment")
    def test_import_env(
            self, mock_env, mock_getcwd, mock_import_env
    ):
        mock_getcwd.return_value = sentinel.cwd
        result = self.runner.invoke(cli.cli, ["import-env", "dev"])
        assert 0 == result.exit_code
        mock_env.assert_called_with(
            sceptre_dir=sentinel.cwd,
            environment_path=u'dev',
            options={}
        )
        mock_import_env.assert_called_with(
            mock_env.return_value
        )

    @patch("sceptre_migration_tool.cli.migrator.import_list")
    @patch("sceptre_migration_tool.cli.open")
    @patch("sceptre_migration_tool.cli.os.getcwd")
    def test_import_list(
            self, mock_getcwd, mock_open, mock_import_list
    ):
        mock_getcwd.return_value = sentinel.cwd
        result = self.runner.invoke(cli.cli, [
            "import-list", "--list-path", "fake-list-path"
        ])
        assert 0 == result.exit_code
        mock_import_list.assert_called_once_with(
            sentinel.cwd,
            {},
            mock_open.return_value.__enter__.return_value
        )

    @patch("sceptre_migration_tool.cli.migrator.generate_import_list")
    @patch("sceptre_migration_tool.cli.open")
    @patch("sceptre_migration_tool.cli.Environment")
    @patch("sceptre_migration_tool.cli.os.getcwd")
    def test_generate_import_list(
            self, mock_getcwd, mock_import_env,
            mock_open, mock_generate_import_list
    ):
        mock_getcwd.return_value = sentinel.cwd
        result = self.runner.invoke(cli.cli, [
            "generate-import-list", "dev", "--list-path", "fake-list-path"
        ])
        assert 0 == result.exit_code
        mock_generate_import_list.assert_called_once_with(
            mock_import_env.return_value,
            mock_open.return_value.__enter__.return_value
        )

    @patch("sceptre_migration_tool.cli.migrator.generate_import_list")
    @patch("sceptre_migration_tool.cli.open")
    @patch("sceptre_migration_tool.cli.Environment")
    @patch("sceptre_migration_tool.cli.os.getcwd")
    def test_generate_import_list__to_stdout(
            self, mock_getcwd, mock_import_env,
            mock_open, mock_generate_import_list
    ):
        mock_getcwd.return_value = sentinel.cwd
        result = self.runner.invoke(cli.cli, [
            "generate-import-list", "dev"
        ])
        assert 0 == result.exit_code
        mock_open.assert_not_called()
        mock_generate_import_list.assert_called_once()
