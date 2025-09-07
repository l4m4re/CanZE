import argparse
import json
import pickle
from typing import Dict, List

def parse_log(path: str) -> Dict[str, List[int]]:
    """Parse a raw ELM327 log.

    Returns a mapping of request hex strings to response payload byte lists.
    """
    results: Dict[str, List[int]] = {}
    active_id: str | None = None
    current_req: str | None = None
    buffer: List[int] = []
    expected_len: int | None = None

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('>'):
                cmd = line[1:].strip()
                if cmd.upper().startswith('ATCRA'):
                    parts = cmd.split()
                    if len(parts) >= 2:
                        active_id = parts[1].upper()
                    current_req = None
                elif cmd.upper().startswith('AT'):
                    current_req = None
                else:
                    current_req = ''.join(cmd.split()).upper()
                    buffer = []
                    expected_len = None
            elif line.startswith('<') and current_req:
                content = line[1:].strip()
                # Support both header+spaced bytes (e.g. "7BB 10 1A 61 ...") and
                # payload-only contiguous hex (e.g. "101A6180...") with ATH0.
                parts = content.split()
                can_id_ok = True
                data: List[int] = []
                if len(parts) > 1:
                    # Attempt header+bytes mode
                    try:
                        # First token could be 11-bit (3 hex) or 29-bit (8 hex) CAN id
                        maybe_can = int(parts[0], 16)
                        # If a filter is active, ensure the header matches
                        if active_id and f"{maybe_can:03X}" != active_id and f"{maybe_can:08X}" != active_id:
                            can_id_ok = False
                        else:
                            data = [int(p, 16) for p in parts[1:]]
                    except ValueError:
                        can_id_ok = True
                        # Fall back to payload-only parsing below
                if not data and can_id_ok:
                    # Payload-only or single-token reply: strip non-hex and parse as contiguous bytes
                    hex_only = ''.join(ch for ch in content if ch.upper() in '0123456789ABCDEF')
                    if len(hex_only) >= 2 and len(hex_only) % 2 == 0:
                        try:
                            data = [int(hex_only[i:i+2], 16) for i in range(0, len(hex_only), 2)]
                        except ValueError:
                            data = []
                if not data or not can_id_ok:
                    continue
                if expected_len is None:
                    if not data:
                        continue
                    pci = data[0]
                    frame_type = pci >> 4
                    if frame_type == 0:  # single frame
                        length = pci & 0x0F
                        results[current_req] = data[1:1 + length]
                        current_req = None
                    elif frame_type == 1:  # first frame
                        expected_len = ((pci & 0x0F) << 8) | data[1]
                        buffer.extend(data[2:])
                    else:
                        continue
                else:
                    pci = data[0]
                    frame_type = pci >> 4
                    if frame_type == 2:  # consecutive frame
                        buffer.extend(data[1:])
                        if len(buffer) >= expected_len:
                            results[current_req] = buffer[:expected_len]
                            current_req = None
                            expected_len = None
                    else:
                        continue
    return results

def main() -> None:
    parser = argparse.ArgumentParser(description="Parse ELM327 .raw logs")
    parser.add_argument("input", help="raw log to parse")
    parser.add_argument("--json", help="write output as JSON")
    parser.add_argument("--pickle", help="write output as a pickle")
    args = parser.parse_args()
    data = parse_log(args.input)
    if args.json:
        with open(args.json, "w") as f:
            json.dump(data, f, indent=2)
    if args.pickle:
        with open(args.pickle, "wb") as f:
            pickle.dump(data, f)
    if not args.json and not args.pickle:
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
