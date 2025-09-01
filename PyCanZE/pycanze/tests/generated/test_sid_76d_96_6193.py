from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_96_6193():
    client = ReplayUDSClient(sid_responses={"2193": ['100E61938001EC00', '210001AE02030119', '2280000000000000']})
    assert client.read_field("76d.96.6193") == pytest.approx(25.0)
