from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62335c():
    client = ReplayUDSClient(sid_responses={"22335C": ['0762335C0014FA68']})
    assert client.read_field("7ec.24.62335c") == pytest.approx(1374824.0)
