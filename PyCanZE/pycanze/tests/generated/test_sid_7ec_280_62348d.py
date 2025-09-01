from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_280_62348d():
    client = ReplayUDSClient(sid_responses={"22348D": ['102B62348D2C9A2D', '21602DCC2DE12DFF', '222D402E342DD22E', '23042E652DCE2DD5', '242DD62DA92E172D', '25F52E5C2DD72DE5', '262DD2AAAAAAAAAA']})
    assert client.read_field("7ec.280.62348d") == pytest.approx(11.868)
