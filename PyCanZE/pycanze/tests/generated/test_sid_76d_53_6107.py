from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_53_6107():
    client = ReplayUDSClient(sid_responses={"2107": ['100A610780F3C9B3', '219132E0D5000000']})
    assert client.read_field("76d.53.6107") == pytest.approx(190.0)
