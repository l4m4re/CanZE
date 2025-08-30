"""Parsers for the CSV database files."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterator, List, Tuple

from .models import Ecu, Frame, Field

DATA_DIR = Path(__file__).resolve().parent / "data"


def _read_csv(path: Path) -> Iterator[List[str]]:
    """Yield rows from *path*.

    Treat lines that start with '#' (after optional whitespace) as comments.
    Do not strip inline '#' characters, as they are part of some field names.
    """
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            if not raw:
                continue
            # Skip pure comment lines
            if raw.lstrip().startswith("#"):
                continue
            line = raw.strip()
            if not line:
                continue
            yield [col.strip() for col in line.split(",")]


            
def _auto_int(value: str) -> int:
    base = 16 if any(c in "abcdefABCDEF" for c in value) else 10
    return int(value, base)


  
def load_ecus(base_dir: Path = DATA_DIR) -> Dict[int, Ecu]:
    """Parse all ``_Ecus.csv`` files found in *base_dir*.

    Returns a mapping of SID to :class:`Ecu`.
    """

    ecus: Dict[int, Ecu] = {}
    for vehicle_dir in base_dir.iterdir():
        csv_file = vehicle_dir / "_Ecus.csv"
        if not csv_file.exists():
            continue
        for row in _read_csv(csv_file):
            name = row[0]
            sid = int(row[1])
            networks = row[2].split(";") if len(row) > 2 and row[2] else []
            request_id = _auto_int(row[3])
            response_id = _auto_int(row[4])
            mnemonic = row[5]
            aliases = row[6].split(";") if len(row) > 6 and row[6] else []
            dtc_response_ids = [
                _auto_int(x) for x in row[7].split(";") if x
            ] if len(row) > 7 else []
            start_diag = _auto_int(row[8]) if len(row) > 8 and row[8] else None
            session_required = int(row[9]) if len(row) > 9 and row[9] else 0
            # Avoid overwriting when multiple ECUs share the same SID (e.g., LBC/LBC2)
            key = sid
            while key in ecus:
                key += 1
            ecus[key] = Ecu(
                name=name,
                sid=sid,
                networks=networks,
                request_id=request_id,
                response_id=response_id,
                mnemonic=mnemonic,
                aliases=aliases,
                dtc_response_ids=dtc_response_ids,
                start_diag=start_diag,
                session_required=session_required,
            )
    return ecus


def load_frames(base_dir: Path = DATA_DIR) -> Dict[int, Frame]:
    """Parse ``_Frames.csv`` files and return a mapping by frame id."""

    frames: Dict[int, Frame] = {}
    for vehicle_dir in base_dir.iterdir():
        csv_file = vehicle_dir / "_Frames.csv"
        if not csv_file.exists():
            continue
        for row in _read_csv(csv_file):
            frame_id = _auto_int(row[0])
            interval_zoe = int(row[1])
            interval_flukan = int(row[2])
            ecu = row[3]
            frames[frame_id] = Frame(
                frame_id=frame_id,
                interval_zoe=interval_zoe,
                interval_flukan=interval_flukan,
                ecu=ecu,
            )
    return frames


def load_fields(base_dir: Path = DATA_DIR) -> Tuple[Dict[str, Field], Dict[str, Field]]:
    """Parse ``*_Fields.csv`` files.

    Returns two dictionaries: by SID and by field name.
    """

    by_sid: Dict[str, Field] = {}
    by_name: Dict[str, Field] = {}

    for vehicle_dir in base_dir.iterdir():
        for csv_file in vehicle_dir.glob("*_Fields.csv"):
            for row in _read_csv(csv_file):
                row += [""] * (13 - len(row))
                (
                    sid,
                    frame_id_s,
                    start_bit_s,
                    end_bit_s,
                    resolution_s,
                    offset_s,
                    decimals_s,
                    unit,
                    request_id,
                    response_id,
                    options_s,
                    name,
                    raw_values,
                ) = row[:13]

                frame_id = _auto_int(frame_id_s) if frame_id_s else 0
                start_bit = int(start_bit_s)
                end_bit = int(end_bit_s)
                resolution = float(resolution_s) if resolution_s else 1.0
                offset = float(offset_s) if offset_s else 0.0
                decimals = int(decimals_s) if decimals_s else 0
                options = [options_s[i : i + 2] for i in range(0, len(options_s), 2)] if options_s else []
                sid = sid or f"{frame_id_s}.{start_bit_s}.{response_id}"
                field = Field(
                    sid=sid,
                    frame_id=frame_id,
                    start_bit=start_bit,
                    end_bit=end_bit,
                    resolution=resolution,
                    offset=offset,
                    decimals=decimals,
                    unit=unit,
                    request_id=request_id or None,
                    response_id=response_id or None,
                    options=options,
                    name=name or None,
                    raw_values=raw_values or None,
                )
                by_sid[sid] = field
                if field.name:
                    by_name[field.name] = field

    return by_sid, by_name


def load_database(base_dir: Path = DATA_DIR):
    """Convenience loader returning all parsed structures."""

    ecus = load_ecus(base_dir)
    frames = load_frames(base_dir)
    fields_by_sid, fields_by_name = load_fields(base_dir)
    return {
        "ecus": ecus,
        "frames": frames,
        "fields_by_sid": fields_by_sid,
        "fields_by_name": fields_by_name,
    }
