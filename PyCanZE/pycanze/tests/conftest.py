from pathlib import Path

from pycanze.tests.test_sid_decoding import MISSING_DB_SIDS, MISMATCHES, SKIPPED_SIDS


def pytest_sessionfinish(session, exitstatus):
    """Emit a summary of missing SIDs and decoding mismatches."""
    if MISSING_DB_SIDS:
        print("\nSIDs missing from CSV definitions:")
        for sid in sorted(MISSING_DB_SIDS):
            print(f"  {sid}")
    if SKIPPED_SIDS:
        print("\nSIDs missing from logs:")
        for sid, name in sorted(SKIPPED_SIDS.items()):
            print(f"  {sid}\t{name}")
    if MISMATCHES:
        print("\nSIDs with decoding mismatches:")
        print("SID\tName\tExpected\tActual\tUnit")
        for sid, (expected, actual, unit, name) in sorted(MISMATCHES.items()):
            print(f"{sid}\t{name}\t{expected}\t{actual}\t{unit}")
    if not MISSING_DB_SIDS and not MISMATCHES and not SKIPPED_SIDS:
        print("\nAll SIDs accounted for and decoded correctly.")

    root = Path(__file__).resolve().parent
    (root / "decoding_skipped_sids.txt").write_text(
        "\n".join(f"{sid}\t{name}" for sid, name in sorted(SKIPPED_SIDS.items())) + ("\n" if SKIPPED_SIDS else "")
    )
    (root / "decoding_mismatches.txt").write_text(
        "\n".join(
            f"{sid}\t{name}\t{expected}\t{actual}\t{unit}"
            for sid, (expected, actual, unit, name) in sorted(MISMATCHES.items())
        )
        + ("\n" if MISMATCHES else "")
    )
