from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_128_6142():
    client = ReplayUDSClient(sid_responses={"2142": ['104A61420E500E50', '210E520E4B0E4C0E', '224D0E500E4D0E4C', '230E4D0E4F0E4D0E', '24500E4D0E4D0E4F', '250E4D0E4F0E510E', '26530E4F0E500E4D', '270E480E4B0E4C0E', '284F0E4C0E4C0E4F', '290E4D0E4D0E500E', '2A4F895989810000']})
    assert client.read_field("7bb.128.6142") == pytest.approx(3.661)
