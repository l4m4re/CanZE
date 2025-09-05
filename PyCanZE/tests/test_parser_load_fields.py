from pathlib import Path

from pycanze.parser import load_fields


def test_specific_fields_override_generic(tmp_path):
    veh = tmp_path / "VEH"
    veh.mkdir()
    # generic definition
    (veh / "_Fields.csv").write_text(
        "sid1,1,0,7,1,0,0,,221234,621234,,generic,\n"
    )
    # ECU specific override
    (veh / "EVC_Fields.csv").write_text(
        "sid1,1,0,7,2,1,0,,221234,621234,,override,\n"
    )
    by_sid, by_name = load_fields(tmp_path, vehicle="VEH")
    field = by_sid["sid1"]
    assert field.resolution == 2.0
    assert field.offset == 1.0
    assert field.name == "override"
    # by_name should also reference overridden field
    assert by_name["override"] is field
