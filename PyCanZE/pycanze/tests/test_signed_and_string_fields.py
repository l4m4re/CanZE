from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest
from pycanze.parser import load_fields


def test_signed_field_sign_extension():
    by_sid, _ = load_fields()
    client = ReplayUDSClient(
        sid_responses={"223018": ["05623018FFF6"]}, fields=by_sid
    )
    assert client.read_field("77e.24.623018") == pytest.approx(-0.16)


def test_string_field_decoding():
    by_sid, _ = load_fields()
    client = ReplayUDSClient(
        sid_responses={
            "2181": [
                "1015618156463141",
                "2147565946303630",
                "22343839313133FF",
                "23D3AAAAAAAAAAAA",
            ]
        },
        fields=by_sid,
    )
    assert client.read_field("7ec.16.6181") == "VF1AGVYF060489113"
