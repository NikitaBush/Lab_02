import json

from streamstats.analysis import Stats
from streamstats.models import make_event
from streamstats.report import build_report, write_json_report

def test_report(tmp_path):
    stats = Stats()
    for level, source in [("ERROR", "база"), ("INFO", "web"), ("CRITICAL", "база")]:
        event = {"timestamp": "2026-10-07T12:00:00+03:00", "level": level,
                 "source": source, "message": "m"}
        stats.add(make_event(event))
    report = build_report(stats)
    assert report["total_events"] == 3
    assert report["top_error_sources"] == [{"source": "база", "count": 2}]

    path = tmp_path / "report.json"
    write_json_report(report, path)
    text = path.read_text(encoding="utf-8")
    assert "база" in text
    assert json.loads(text) == report