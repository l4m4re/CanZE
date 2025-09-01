from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620711():
    client = ReplayUDSClient(sid_responses={"220711": ['0462071100000000']})
    assert client.read_field("76d.24.620711") == pytest.approx(0.16)
