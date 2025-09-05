import os
import tempfile
import unittest

from pycanze.log_parser import parse_log

class LogParserTest(unittest.TestCase):
    def test_multiframe_assembly(self) -> None:
        sample = (
            "> ATZ\n"
            "< ELM327 v2.1\n"
            "> ATCRA 7E8\n"
            "< OK\n"
            "> 7DF 02 10 03\n"
            "< 7E8 10 0C 61 00 11 22 33 44\n"
            "< 7E8 21 55 66 77 88 99 AA\n"
        )
        with tempfile.NamedTemporaryFile('w+', delete=False) as f:
            f.write(sample)
            fname = f.name
        try:
            parsed = parse_log(fname)
            self.assertEqual(parsed["7DF021003"], [
                0x61, 0x00, 0x11, 0x22, 0x33, 0x44,
                0x55, 0x66, 0x77, 0x88, 0x99, 0xAA,
            ])
        finally:
            os.unlink(fname)

if __name__ == "__main__":
    unittest.main()
