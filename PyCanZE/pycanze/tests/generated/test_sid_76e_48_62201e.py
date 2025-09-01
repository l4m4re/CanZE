from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_48_62201e():
    client = ReplayUDSClient(sid_responses={"22201E": ['100A62201E1E783C', '21783C783C1E783C']})
    assert client.read_field("76e.48.62201e") == pytest.approx(120.0)
