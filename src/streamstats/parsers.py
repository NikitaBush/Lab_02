"""Парсеры CSV и JSONL."""

import csv
import json

from streamstats.errors import InvalidEventError, UnsupportedFormatError
from streamstats.models import make_event


def to_event(data):
    try:
        return make_event(data)
    except InvalidEventError as error:
        return error


def parse_jsonl(path):
    with open(path, encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if line.strip() == "":
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                yield line_number, InvalidEventError("некорректный JSON")
                continue
            yield line_number, to_event(data)


def parse_csv(path):
    with open(path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # запись в кавычках может занимать несколько строк файла
            line_number = reader.line_num
            if None in row:
                yield line_number, InvalidEventError("лишние значения в строке")
                continue
            # если значений не хватает, DictReader ставит None — поля нет
            data = {key: value for key, value in row.items() if value is not None}
            yield line_number, to_event(data)


PARSERS = {"csv": parse_csv, "jsonl": parse_jsonl}


def get_parser(name):
    if name not in PARSERS:
        raise UnsupportedFormatError(f"формат '{name}' не поддерживается")
    return PARSERS[name]
