from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620706():
    client = ReplayUDSClient(sid_responses={"220706": ['0462070600000000']})
    assert client.read_field("76d.24.620706") == pytest.approx(0.1)
