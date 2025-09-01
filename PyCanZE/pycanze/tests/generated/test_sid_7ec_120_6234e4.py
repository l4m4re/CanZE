from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_120_6234e4():
    client = ReplayUDSClient(sid_responses={"2234E4": ['10176234E4000D00', '210D000D00180019', '22000E000D000D00', '230D000DAAAAAAAA']})
    assert client.read_field("7ec.120.6234e4") == pytest.approx(1.3)
