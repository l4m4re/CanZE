from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623366():
    client = ReplayUDSClient(sid_responses={"223366": ['076233660026D163']})
    assert client.read_field("7ec.24.623366") == pytest.approx(2543971.0)
