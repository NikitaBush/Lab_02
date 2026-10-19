import pytest

from streamstats.errors import InvalidEventError, UnsupportedFormatError
from streamstats.models import Event
from streamstats.parsers import get_parser, parse_csv, parse_jsonl

HEADER = "timestamp,level,source,message\n"


def test_csv(write_file):
    path = write_file(
        "a.csv",
        HEADER
        + '2026-10-07T12:00:00+03:00,INFO,loader,"Книги, чтение"\n'
        + "2026-10-07T12:01:00+03:00,ERROR,db,Упало\n",
    )
    result = list(parse_csv(path))
    assert [number for number, _ in result] == [2, 3]
    assert result[0][1].message == "Книги, чтение"
    assert result[1][1].level == "ERROR"


def test_csv_missing_and_empty(write_file):
    path = write_file(
        "a.csv",
        HEADER + "2026-10-07T12:00:00Z,INFO,loader\n" + "2026-10-07T12:00:00Z,INFO,,текст\n",
    )
    result = list(parse_csv(path))
    assert "нет обязательного поля" in str(result[0][1])
    assert "пустое" in str(result[1][1])


def test_jsonl(write_file):
    path = write_file(
        "a.jsonl",
        '{"timestamp":"2026-10-07T12:00:00Z","level":"INFO","source":"a","message":"m"}\n'
        "{сломано\n"
        '{"timestamp":"2026-10-07T12:00:00Z","level":"DEBUG","source":"b","message":"m"}\n',
    )
    result = list(parse_jsonl(path))
    assert [number for number, _ in result] == [1, 2, 3]
    assert isinstance(result[0][1], Event)
    assert isinstance(result[1][1], InvalidEventError)
    assert result[2][1].level == "DEBUG"


def test_get_parser():
    assert get_parser("csv") is parse_csv
    with pytest.raises(UnsupportedFormatError):
        get_parser("xml")
