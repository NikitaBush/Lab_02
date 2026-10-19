"""Исключения пакета streamstats."""


class StreamStatsError(Exception):
    """Базовая ошибка пакета."""


class UnsupportedFormatError(StreamStatsError):
    """Неподдерживаемый формат файла."""


class InvalidEventError(StreamStatsError):
    """Неверное событие. Файл и строку дописываем, когда они известны."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.path = None
        self.line_number = None
        self.file_index = None

    def __str__(self):
        if self.path is None:
            return self.message
        return f"файл №{self.file_index} ({self.path}), строка {self.line_number}: {self.message}"


class InvalidTimestampError(InvalidEventError):
    """Неверная временная метка."""


class CliConfigError(StreamStatsError):
    """Ошибка аргументов командной строки."""
