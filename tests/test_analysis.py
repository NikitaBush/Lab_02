import json

import pytest

from streamstats.analysis import analyze
from streamstats.errors import InvalidEventError
from streamstats.models import parse_timestamp


def line(ts, level, source):
    data = {"timestamp": ts, "level": level, "source": source, "message": "m"}
    return json.dumps(data, ensure_ascii=False) + "\n"

BROKEN = (
    line("2026-10-07T12:00:00Z", "INFO", "a")
    + "{битая строка\n"
    + line("2026-10-07T12:02:00Z", "ERROR", "b")
)


def test_empty_file(write_file):
    stats = analyze([write_file("empty.jsonl", "")], "jsonl")
    assert stats.total == 0
    assert stats.first is None


def test_counts(write_file):
    path = write_file(
        "a.jsonl",
        line("2026-10-07T12:00:00Z", "INFO", "web")
        + line("2026-10-07T12:01:00Z", "ERROR", "web")
        + line("2026-10-07T12:02:00Z", "CRITICAL", "db"),
    )
    stats = analyze([path], "jsonl")
    assert stats.total == 3
    assert stats.levels["INFO"] == 1
    assert stats.sources == {"web": 2, "db": 1}
    assert stats.top_error_sources() == [("db", 1), ("web", 1)]


def test_several_files(write_file):
    a = write_file("a.jsonl", line("2026-10-07T12:00:00Z", "ERROR", "db"))
    b = write_file("b.jsonl", line("2026-10-08T12:00:00Z", "ERROR", "db"))
    stats = analyze([a, b], "jsonl")
    assert stats.total == 2
    assert stats.error_sources == {"db": 2}
    assert stats.first == parse_timestamp("2026-10-07T12:00:00Z")
    assert stats.last == parse_timestamp("2026-10-08T12:00:00Z")


def test_broken_line_stops(write_file):
    bad = write_file("bad.jsonl", BROKEN)
    with pytest.raises(InvalidEventError) as info:
        analyze([bad], "jsonl")
    assert info.value.line_number == 2
    assert "bad.jsonl" in str(info.value)


def test_broken_line_skipped(write_file):
    bad = write_file("bad.jsonl", BROKEN)
    stats = analyze([bad], "jsonl", skip_invalid=True)
    assert stats.total == 2
    assert stats.skipped == 1


def test_broken_csv_line(write_file):
    path = write_file(
        "a.csv",
        "timestamp,level,source,message\n"
        "2026-10-07T12:00:00Z,INFO,a,ok\n"
        "2026-10-07T12:00:00Z,NOPE,a,плохой уровень\n",
    )
    with pytest.raises(InvalidEventError):
        analyze([path], "csv")
    assert analyze([path], "csv", skip_invalid=True).skipped == 1


def test_unicode(write_file):
    path = write_file("юникод.jsonl", line("2026-10-07T12:00:00Z", "ERROR", "платёжный-шлюз"))
    stats = analyze([path], "jsonl")
    assert stats.top_error_sources() == [("платёжный-шлюз", 1)]
