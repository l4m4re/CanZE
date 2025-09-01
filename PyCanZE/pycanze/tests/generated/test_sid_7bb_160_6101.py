from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_160_6101():
    client = ReplayUDSClient(sid_responses={"2101": ['1034610113AB138D', '2100000000000000', '2200000000000992', '230D6110CC2A0900', '2400053F00000000', '2500000007147F00', '26000F8A29270F00', '2700000000000000']})
    assert client.read_field("7bb.160.6101") == pytest.approx(3425.0)
