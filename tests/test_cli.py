import sys

from runrelay.cli import main


def test_cli_submit_and_list(tmp_path, capsys):
    main(
        [
            "--home",
            str(tmp_path),
            "submit",
            "--command",
            f'"{sys.executable}" -c "print(789)"',
        ]
    )
    output = capsys.readouterr().out
    assert "Experiment submitted" in output
    main(["--home", str(tmp_path), "list"])
    output = capsys.readouterr().out
    assert "STATUS" in output
