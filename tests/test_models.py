import pytest

from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.models import make_event, parse_timestamp


def good():
    return {
        "timestamp": "2026-10-07T12:00:00+03:00",
        "level": "INFO",
        "source": "loader",
        "message": "Начало чтения",
    }


def test_good_event():
    event = make_event(good())
    assert event.level == "INFO"
    assert event.source == "loader"


def test_missing_field():
    data = good()
    del data["source"]
    with pytest.raises(InvalidEventError, match="нет обязательного поля"):
        make_event(data)


def test_empty_field():
    data = good()
    data["source"] = ""
    with pytest.raises(InvalidEventError, match="пустое"):
        make_event(data)


def test_empty_message_is_ok():
    data = good()
    data["message"] = ""
    assert make_event(data).message == ""


def test_bad_level():
    data = good()
    data["level"] = "FATAL"
    with pytest.raises(InvalidEventError):
        make_event(data)


def test_bad_timestamp():
    data = good()
    data["timestamp"] = "вчера"
    with pytest.raises(InvalidTimestampError):
        make_event(data)


def test_timezones():
    assert parse_timestamp("2026-10-07T12:00:00+03:00") == parse_timestamp("2026-10-07T09:00:00Z")