from pycanze.tests.test_sid_decoding import MISSING_DB_SIDS, MISMATCHES


def pytest_sessionfinish(session, exitstatus):
    """Emit a summary of missing SIDs and decoding mismatches."""
    if MISSING_DB_SIDS:
        print("\nSIDs missing from CSV definitions:")
        for sid in sorted(MISSING_DB_SIDS):
            print(f"  {sid}")
    if MISMATCHES:
        print("\nSIDs with decoding mismatches:")
        print("SID\tExpected\tActual\tUnit")
        for sid, (expected, actual, unit) in sorted(MISMATCHES.items()):
            print(f"{sid}\t{expected}\t{actual}\t{unit}")
    if not MISSING_DB_SIDS and not MISMATCHES:
        print("\nAll SIDs accounted for and decoded correctly.")
