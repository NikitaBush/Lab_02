import json

from streamstats.__main__ import main

GOOD = (
    '{"timestamp":"2026-10-07T12:00:00+03:00","level":"ERROR","source":"база","message":"x"}\n'
    '{"timestamp":"2026-10-07T12:01:00+03:00","level":"INFO","source":"web","message":"y"}\n'
)
BAD = GOOD + "{сломано\n" + GOOD


def test_cli_ok(tmp_path, write_file, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_file("a.jsonl", GOOD)
    write_file("b.jsonl", GOOD)
    code = main(["analyze", "a.jsonl", "b.jsonl", "--format", "jsonl", "--output", "out.json"])
    assert code == 0
    report = json.loads((tmp_path / "out.json").read_text(encoding="utf-8"))
    assert report["total_events"] == 4
    assert (tmp_path / "streamstats.log").exists()


def test_cli_broken_line(tmp_path, write_file, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    write_file("bad.jsonl", BAD)
    assert main(["analyze", "bad.jsonl", "--format", "jsonl"]) == 2
    assert "строка 3" in capsys.readouterr().err
    assert not (tmp_path / "report.json").exists()


def test_cli_skip_invalid(tmp_path, write_file, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_file("bad.jsonl", BAD)
    assert main(["analyze", "bad.jsonl", "--format", "jsonl", "--skip-invalid"]) == 0
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert report["skipped_lines"] == 1
    assert "WARNING" in (tmp_path / "streamstats.log").read_text(encoding="utf-8")


def test_cli_bad_args(tmp_path, write_file, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_file("a.jsonl", GOOD)
    assert main(["analyze", "a.jsonl", "--format", "xml"]) == 2
    assert main(["analyze", "nope.jsonl", "--format", "jsonl"]) == 2
