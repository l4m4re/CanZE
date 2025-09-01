from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_80_6134():
    client = ReplayUDSClient(sid_responses={"2134": ['1022613421CCFC07', '21023D3D0021CAE6', '2200003E3E0021CC', '23E600003E3E0021', '24CCE600003F3F00']})
    assert client.read_field("7bb.80.6134") == pytest.approx(1.0)
