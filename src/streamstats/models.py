"""Модель события и проверка полей."""

from dataclasses import dataclass
from datetime import datetime, timezone

from streamstats.errors import InvalidEventError, InvalidTimestampError

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
ERROR_LEVELS = ["ERROR", "CRITICAL"]
REQUIRED_FIELDS = ["timestamp", "level", "source", "message"]


@dataclass
class Event:
    timestamp: datetime
    level: str
    source: str
    message: str


def parse_timestamp(value):
    if not isinstance(value, str):
        raise InvalidTimestampError("поле 'timestamp' должно быть строкой")
    try:
        result = datetime.fromisoformat(value)
    except ValueError as error:
        raise InvalidTimestampError(f"поле 'timestamp' не в формате ISO 8601: {value}") from error
    # без пояса считаем UTC, иначе не сравнить с датами, где пояс указан
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result


def make_event(data):
    if not isinstance(data, dict):
        raise InvalidEventError("запись должна быть объектом")

    for name in REQUIRED_FIELDS:
        if name not in data:
            raise InvalidEventError(f"нет обязательного поля '{name}'")
        if not isinstance(data[name], str):
            raise InvalidEventError(f"поле '{name}' должно быть строкой")

    for name in ["timestamp", "level", "source"]:
        if data[name].strip() == "":
            raise InvalidEventError(f"поле '{name}' пустое")

    timestamp = parse_timestamp(data["timestamp"])

    level = data["level"]
    if level not in LEVELS:
        raise InvalidEventError(f"недопустимый уровень '{level}'")

    return Event(timestamp, level, data["source"], data["message"])
