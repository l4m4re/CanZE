from pycanze.parser import load_fields


def test_field_bitmask_parsing_and_predicates():
    by_sid, by_name = load_fields(vehicle="ZOE_Ph2")
    signed = by_sid["1f8.40"]
    assert signed.options == int("1ff", 16)
    assert signed.is_signed()
    assert not signed.is_string()
    assert not signed.is_hex_string()

    hexfield = by_name["DTCRecord"]
    assert hexfield.options == int("4ff", 16)
    assert hexfield.is_hex_string()
