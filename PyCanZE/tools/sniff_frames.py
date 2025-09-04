#!/usr/bin/env python3
"""Simple CLI to sniff raw CAN frames using UDSClient.start_sniffing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from repository root without installation
sys.path.append(str(Path(__file__).resolve().parent.parent))
from pycanze import UDSClient  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sniff raw CAN frames via ATMA")
    parser.add_argument("--host", default="192.168.2.21", help="ELM327 host")
    parser.add_argument("--port", type=int, default=35000, help="ELM327 TCP port")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = UDSClient(args.host, port=args.port)
    client.connect()
    client.initialize()
    try:
        for fid, payload in client.start_sniffing():
            payload_hex = " ".join(f"{b:02X}" for b in payload)
            print(f"{fid:03X} {payload_hex}")
    except KeyboardInterrupt:
        pass
    finally:
        client.stop_sniffing()
        client.close()


if __name__ == "__main__":
    main()
