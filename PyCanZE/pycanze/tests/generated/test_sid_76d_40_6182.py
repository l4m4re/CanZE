from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_40_6182():
    client = ReplayUDSClient(sid_responses={"2182": ['103E618295050000', '21FFFF0100FFFFFF', '22FFFFFFFFFFFFFF', '23FFFFFFFFFF00FF', '24FFFFFFFFFFFFFF', '25FFFFFFFFFFFFFF', '26FFFFFFFFFFFFFF', '27FFFFFFFFFFFFFF', '28FFFFFFFFFFFFFF']})
    assert client.read_field("76d.40.6182") == pytest.approx(0.0)
