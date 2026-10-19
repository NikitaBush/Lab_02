"""Подсчёт статистики. События в список не сохраняются, только счётчики."""

import logging
from collections import Counter

from streamstats.errors import InvalidEventError
from streamstats.models import ERROR_LEVELS, LEVELS
from streamstats.parsers import get_parser

logger = logging.getLogger("streamstats")


class Stats:
    def __init__(self):
        self.total = 0
        self.skipped = 0
        self.levels = {level: 0 for level in LEVELS}
        self.sources = Counter()
        self.error_sources = Counter()
        self.first = None
        self.last = None

    def add(self, event):
        self.total += 1
        self.levels[event.level] += 1
        self.sources[event.source] += 1
        if event.level in ERROR_LEVELS:
            self.error_sources[event.source] += 1
        if self.first is None or event.timestamp < self.first:
            self.first = event.timestamp
        if self.last is None or event.timestamp > self.last:
            self.last = event.timestamp

    def top_error_sources(self, count=5):
        # при равном числе ошибок — по имени, чтобы порядок не зависел от входа
        pairs = sorted(self.error_sources.items(), key=lambda pair: (-pair[1], pair[0]))
        return pairs[:count]


def analyze(paths, file_format, skip_invalid=False):
    parser = get_parser(file_format)
    stats = Stats()
    for file_index, path in enumerate(paths, start=1):
        logger.info("Читаю файл %s", path)
        for line_number, item in parser(path):
            if isinstance(item, InvalidEventError):
                item.path = path
                item.file_index = file_index
                item.line_number = line_number
                if not skip_invalid:
                    raise item
                stats.skipped += 1
                logger.warning("Пропуск: %s", item)
                continue
            stats.add(item)
    logger.info("Событий: %d, пропущено: %d", stats.total, stats.skipped)
    return stats
