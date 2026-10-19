"""CLI: python -m streamstats analyze ..."""

import argparse
import logging
import sys
from pathlib import Path

from streamstats.analysis import analyze
from streamstats.errors import CliConfigError, StreamStatsError
from streamstats.report import build_report, write_json_report

logger = logging.getLogger("streamstats")


def build_arg_parser():
    parser = argparse.ArgumentParser(prog="streamstats", description="Анализ событий CSV и JSONL")
    commands = parser.add_subparsers(dest="command", required=True)
    cmd = commands.add_parser("analyze", help="посчитать статистику и сохранить отчёт")
    cmd.add_argument("inputs", nargs="+", metavar="INPUT", help="входные файлы")
    cmd.add_argument("--format", dest="file_format", required=True, help="csv или jsonl")
    cmd.add_argument("--output", default="report.json", help="файл отчёта")
    cmd.add_argument("--skip-invalid", action="store_true", help="пропускать ошибочные строки")
    return parser


def setup_logging():
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.propagate = False

    file_handler = logging.FileHandler("streamstats.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(file_handler)

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.WARNING)
    console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(console)
    return file_handler


def main(argv=None):
    args = build_arg_parser().parse_args(argv)
    file_handler = setup_logging()
    try:
        for name in args.inputs:
            if not Path(name).is_file():
                raise CliConfigError(f"файл не найден: {name}")
        stats = analyze(args.inputs, args.file_format, args.skip_invalid)
        write_json_report(build_report(stats), args.output)
        logger.info("Отчёт сохранён: %s", args.output)
        print(f"Отчёт сохранён: {args.output}")
        return 0
    except StreamStatsError as error:
        logger.error("%s", error)
        return 2
    finally:
        file_handler.close()


if __name__ == "__main__":
    sys.exit(main())
