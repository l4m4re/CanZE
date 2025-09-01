from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_20_6106():
    client = ReplayUDSClient(sid_responses={"2106": ['10176106D0C056FF', '21967E386BB03231', '22060203008F1439', '23BEF7FB00000000']})
    assert client.read_field("76d.20.6106") == pytest.approx(0.0)
