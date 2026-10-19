"""JSON-отчёт."""

import json


def build_report(stats):
    return {
        "total_events": stats.total,
        "skipped_lines": stats.skipped,
        "levels": stats.levels,
        "sources": dict(sorted(stats.sources.items())),
        "top_error_sources": [
            {"source": source, "count": count} for source, count in stats.top_error_sources()
        ],
        "first_timestamp": stats.first.isoformat() if stats.first else None,
        "last_timestamp": stats.last.isoformat() if stats.last else None,
    }


def write_json_report(report, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)