import unittest
from pycanze.uds import UDSClient, ELM_CMD_SLEEP

class DummyClient(UDSClient):
    def __init__(self):
        super().__init__('0.0.0.0')
        self.sock = object()
        self._read_calls = 0
    def _send(self, line: str, wait: float = ELM_CMD_SLEEP) -> None:
        pass
    def _read_lines(self, timeout: float | None = None):
        self._read_calls += 1
        if self._read_calls == 1:
            return [
                '10 0D 61 03 11 22 33 44',
                '21 55 66 77 88 99 AA BB'
            ]
        return []

class IsoTpReassemblyTest(unittest.TestCase):
    def test_collects_consecutive_frames_present_in_first_read(self):
        cli = DummyClient()
        resp = cli._read_by_id(0x21, 0x03, 1)
        self.assertEqual(resp, [
            0x61, 0x03, 0x11, 0x22, 0x33, 0x44,
            0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB
        ])

if __name__ == '__main__':
    unittest.main()
