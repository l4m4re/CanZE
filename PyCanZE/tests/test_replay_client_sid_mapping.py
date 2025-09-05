
def test_accepts_sid_mapping(mk_replay_client):
    cli = mk_replay_client(sid_responses={"10C0": ["50C0"]})
    cli._send("0210C0")
    assert cli._read_lines() == ["50C0"]
