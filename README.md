# ЛР № 2. Потоковый анализатор `streamstats`

Читает события из CSV и JSONL построчно, проверяет их и сохраняет статистику в JSON.

## Установка

```bash
pip install -e .
pip install pytest ruff
```

## Запуск

```bash
python -m streamstats analyze data/events.csv --format csv --output report.json
python -m streamstats analyze data/events.jsonl data/broken.jsonl --format jsonl --skip-invalid
```

По умолчанию ошибочная строка останавливает обработку (код выхода 2).
С `--skip-invalid` строка пропускается, в `streamstats.log` пишется WARNING,
а число пропусков попадает в отчёт.

## Проверка

```bash
python -m pytest
ruff check .
python -m streamstats --help
```