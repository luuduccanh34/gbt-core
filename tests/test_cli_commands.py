from click.testing import CliRunner

from core.gbt.cli.main import cli


def test_cli_lists_compile_and_run_commands() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "compile" in result.output
    assert "run" in result.output


def test_compile_command_is_invokable() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["compile", "--help"])

    assert result.exit_code == 0
    assert "--select" in result.output
    assert "--profiles-dir" in result.output
