from pathlib import Path

from click.testing import CliRunner

from pdf_translator.cli import main


def test_cli_rejects_output_equal_to_input(tmp_path: Path):
    input_file = tmp_path / "sample.pdf"
    input_file.write_bytes(b"%PDF-1.4\n")

    runner = CliRunner()
    result = runner.invoke(
        main,
        [str(input_file), "-t", "english", "-o", str(input_file)],
    )

    assert result.exit_code != 0
    assert "Output file must be different from input file." in result.output
