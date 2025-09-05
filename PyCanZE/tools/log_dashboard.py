from __future__ import annotations

import argparse
import csv
import sqlite3
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, render_template_string, request

# Allow running from repository root without installation
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from pycanze.state import SID_HV_V, SID_SOC  # type: ignore


class LogStore:
    """Read rows from rotating CSV or SQLite logs."""

    def __init__(self, csv_path: Optional[Path] = None, sqlite_path: Optional[Path] = None) -> None:
        self.csv_path = csv_path
        self.sqlite_path = sqlite_path

    # ------------------------------------------------------------------
    def _iter_paths(self, base: Path) -> List[Path]:
        pattern = f"{base.stem}*{base.suffix}"
        return sorted(base.parent.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

    def _last_csv(self, limit: int) -> List[Dict[str, Any]]:
        assert self.csv_path
        rows: List[Dict[str, Any]] = []
        remaining = limit
        for path in self._iter_paths(self.csv_path):
            with path.open() as f:
                reader = csv.DictReader(f)
                tail = list(deque(reader, maxlen=remaining))
            rows = tail + rows
            remaining = limit - len(rows)
            if remaining <= 0:
                break
        return rows[-limit:]

    def _last_sqlite(self, limit: int) -> List[Dict[str, Any]]:
        assert self.sqlite_path
        rows: List[Dict[str, Any]] = []
        remaining = limit
        for path in self._iter_paths(self.sqlite_path):
            with sqlite3.connect(path) as conn:
                conn.row_factory = sqlite3.Row
                tail = [dict(r) for r in conn.execute(
                    "SELECT * FROM logs ORDER BY ROWID DESC LIMIT ?", (remaining,)
                ).fetchall()]
                tail.reverse()
            rows = tail + rows
            remaining = limit - len(rows)
            if remaining <= 0:
                break
        return rows[-limit:]

    def last(self, limit: int) -> List[Dict[str, Any]]:
        if self.sqlite_path:
            return self._last_sqlite(limit)
        if self.csv_path:
            return self._last_csv(limit)
        return []


HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>PyCanZE Logs</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
<h1>PyCanZE Logs</h1>
<canvas id="socChart" height="120"></canvas>
<canvas id="hvChart" height="120"></canvas>
<script>
async function load() {
  const resp = await fetch('/samples?n=100');
  const data = await resp.json();
  const labels = data.map(r => r.timestamp);
  const soc = data.map(r => r['{{ soc }}']);
  const hv = data.map(r => r['{{ hv }}']);
  new Chart(document.getElementById('socChart'), {
    type: 'line',
    data: {labels: labels, datasets: [{label: 'SOC', data: soc}]}
  });
  new Chart(document.getElementById('hvChart'), {
    type: 'line',
    data: {labels: labels, datasets: [{label: 'HV Voltage', data: hv}]}
  });
}
load();
</script>
</body>
</html>
"""


def create_app(store: LogStore) -> Flask:
    app = Flask(__name__)

    @app.get("/samples")
    def samples() -> Any:
        limit = int(request.args.get("n", 100))
        return jsonify(store.last(limit))

    @app.get("/")
    def index() -> Any:
        return render_template_string(HTML_TEMPLATE, soc=SID_SOC, hv=SID_HV_V)

    return app


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Serve a simple dashboard for log files")
    p.add_argument("--csv", type=Path)
    p.add_argument("--sqlite", type=Path)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    store = LogStore(csv_path=args.csv, sqlite_path=args.sqlite)
    app = create_app(store)
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
