from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623369():
    client = ReplayUDSClient(sid_responses={"223369": ['076233690014E514']})
    assert client.read_field("7ec.24.623369") == pytest.approx(1369364.0)
