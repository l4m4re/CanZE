from pycanze.models import Field
from pycanze.replay_client import ReplayClient as ReplayUDSClient


def _mk_field(sid, start_bit, end_bit, request_id, options=0):
    return Field(
        sid=sid,
        frame_id=0x7E8,
        start_bit=start_bit,
        end_bit=end_bit,
        resolution=1.0,
        offset=0.0,
        decimals=0,
        unit="",
        request_id=request_id,
        response_id=None,
        options=options,
    )


def test_all_ones_width_ge_5_returns_none():
    field = _mk_field("test.ge5", 24, 31, "220001")
    client = ReplayUDSClient(
        sid_responses={"220001": ["04620001FF"]}, fields={field.sid: field}
    )
    assert client.read_field(field.sid) is None


def test_all_ones_width_le_4_valid():
    field = _mk_field("test.le4", 28, 31, "220002")
    client = ReplayUDSClient(
        sid_responses={"220002": ["046200020F"]}, fields={field.sid: field}
    )
    assert client.read_field(field.sid) == 0xF


def test_string_field_all_ones_returns_none():
    field = _mk_field(
        "test.str", 24, 39, "220003", options=Field.FIELD_TYPE_STRING
    )
    client = ReplayUDSClient(
        sid_responses={"220003": ["05620003FFFF"]}, fields={field.sid: field}
    )
    assert client.read_field(field.sid) is None
