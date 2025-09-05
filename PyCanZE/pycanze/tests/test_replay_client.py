import unittest

from pycanze.replay_client import ReplayClient


class ReplayClientTest(unittest.TestCase):
    def test_accepts_sid_mapping(self):
        cli = ReplayClient(sid_responses={"10C0": ["50C0"]})
        cli._send("0210C0")
        self.assertEqual(cli._read_lines(), ["50C0"])


if __name__ == "__main__":
    unittest.main()
