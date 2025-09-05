#!/usr/bin/env python3
"""Log selected fields to CSV or SQLite with optional rotation."""

from __future__ import annotations

import argparse
import csv
import os
import socket
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

# Allow running from repository root without installation
sys.path.append(str(Path(__file__).resolve().parent.parent))
from pycanze import UDSClient  # type: ignore
from pycanze.parser import load_fields  # type: ignore
from pycanze.state import POLL_SIDS  # type: ignore


class Logger:
    """Persist rows to CSV and/or SQLite with size-based rotation."""

    def __init__(
        self,
        csv_path: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        rotate_kb: Optional[int] = None,
    ) -> None:
        self.csv_path = csv_path
        self.sqlite_path = sqlite_path
        self.rotate_kb = rotate_kb
        self._csv_file: Optional[Any] = None
        self._csv_writer: Optional[csv.DictWriter] = None
        self._sqlite_conn: Optional[sqlite3.Connection] = None
        self._columns: Optional[Iterable[str]] = None

    # ------------------------------------------------------------------
    def _should_rotate(self, path: Path) -> bool:
        return bool(self.rotate_kb and path.exists() and path.stat().st_size >= self.rotate_kb * 1024)

    def _rotate(self, path: Path) -> None:
        ts = time.strftime("%Y%m%d-%H%M%S")
        path.rename(path.with_name(f"{path.stem}-{ts}{path.suffix}"))

    # ------------------------------------------------------------------
    def log(self, row: Dict[str, Any]) -> None:
        if self.csv_path:
            self._log_csv(row)
        if self.sqlite_path:
            self._log_sqlite(row)

    def _log_csv(self, row: Dict[str, Any]) -> None:
        assert self.csv_path
        if self._csv_file is None or self._should_rotate(self.csv_path):
            if self._csv_file:
                self._csv_file.close()
                self._rotate(self.csv_path)
            exists = self.csv_path.exists()
            self._csv_file = self.csv_path.open("a", newline="")
            self._csv_writer = csv.DictWriter(self._csv_file, fieldnames=row.keys())
            if not exists:
                self._csv_writer.writeheader()
        assert self._csv_writer
        self._csv_writer.writerow(row)
        self._csv_file.flush()

    def _log_sqlite(self, row: Dict[str, Any]) -> None:
        assert self.sqlite_path
        if self._sqlite_conn is None or self._should_rotate(self.sqlite_path):
            if self._sqlite_conn:
                self._sqlite_conn.close()
                self._rotate(self.sqlite_path)
            init = not self.sqlite_path.exists()
            self._sqlite_conn = sqlite3.connect(self.sqlite_path)
            self._columns = list(row.keys())
            cols_sql = ", ".join(
                f"{c} REAL" if c != "timestamp" else "timestamp TEXT" for c in self._columns
            )
            if init:
                self._sqlite_conn.execute(f"CREATE TABLE logs ({cols_sql})")
                self._sqlite_conn.commit()
        assert self._sqlite_conn and self._columns
        placeholders = ", ".join("?" for _ in self._columns)
        self._sqlite_conn.execute(
            f"INSERT INTO logs VALUES ({placeholders})", [row[c] for c in self._columns]
        )
        self._sqlite_conn.commit()

    def close(self) -> None:
        if self._csv_file:
            self._csv_file.close()
        if self._sqlite_conn:
            self._sqlite_conn.close()


# ----------------------------------------------------------------------

def _safe_read(client: UDSClient, sid: str) -> Optional[float]:
    try:
        val = client.read_field(sid)
        if isinstance(val, str):
            return None
        return val  # type: ignore[return-value]
    except (TimeoutError, socket.timeout):
        return None
    except (OSError, ConnectionError):
        raise
    except Exception:
        return None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Log diagnostic fields to CSV or SQLite")
    p.add_argument("--host", default=os.environ.get("PYCANZE_HOST", "192.168.2.21"))
    p.add_argument("--port", type=int, default=int(os.environ.get("PYCANZE_PORT", "35000")))
    p.add_argument("--vehicle", default=os.environ.get("PYCANZE_VEHICLE"))
    p.add_argument("--fields", nargs="+", default=list(POLL_SIDS))
    p.add_argument("--interval", type=int, default=300, help="Polling interval in seconds")
    p.add_argument("--csv", type=Path)
    p.add_argument("--sqlite", type=Path)
    p.add_argument("--rotate", type=int, help="Rotate logs when files exceed this size in kB")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    fields = load_fields(vehicle=args.vehicle)[0] if args.vehicle else load_fields()[0]
    client = UDSClient(args.host, port=args.port, fields=fields)
    logger = Logger(args.csv, args.sqlite, args.rotate)
    try:
        while True:
            row: Dict[str, Any] = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}
            for sid in args.fields:
                row[sid] = _safe_read(client, sid)
            logger.log(row)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            client.close()
        finally:
            logger.close()


if __name__ == "__main__":
    main()
