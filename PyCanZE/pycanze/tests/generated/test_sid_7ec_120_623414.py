from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_120_623414():
    client = ReplayUDSClient(sid_responses={"223414": ['1017623414003500', '2135003500350067', '22009D010C010C01', '230C010CAAAAAAAA']})
    assert client.read_field("7ec.120.623414") == pytest.approx(2.68)
