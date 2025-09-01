from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b44():
    client = ReplayUDSClient(sid_responses={"224B44": ['102B624B44013203', '211800A20409009B', '220468013C040C01', '231B0303013B030E', '24009C0407013402', '250701330401013D', '2604530000000000']})
    assert client.read_field("7bc.24.624b44") == pytest.approx(306.0)
