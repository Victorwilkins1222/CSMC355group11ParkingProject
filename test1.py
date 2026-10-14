"""
test1.py - UC01 test cases (Count Cars Entering the Parking Structure)
Group 11 - Parking System

Run:  python test1.py

SECTION 1 is a small stand-in for the lot logic so this file runs on its own.
When your real implementation exists, delete SECTION 1 and import yours instead,
e.g.  from parking import ParkingLot
(The test cases in SECTION 2 only need: .available, .status, and entry(t).)
"""

# ---------------------------------------------------------------------------
# SECTION 1: stand-in implementation of UC01 (replace with your real code)
# ---------------------------------------------------------------------------
DUPLICATE_WINDOW_SECONDS = 2  # BR03


class ParkingLot:
    def __init__(self, lot_id, total_spots, available):
        self.lot_id = lot_id
        self.total_spots = total_spots
        self.available = available
        self.status = "Full" if available == 0 else "Available"
        self.last_signal_time = None

    def entry(self, t):
        """Handle one entry-sensor signal at time t (seconds).
        Returns a message string describing what the system displays."""
        # A02 / BR03: ignore a duplicate signal inside the 2 s window
        if (self.last_signal_time is not None
                and t - self.last_signal_time < DUPLICATE_WINDOW_SECONDS):
            return "Duplicate ignored"

        # E01 / BR01: lot already full, reject and never go below 0
        if self.available <= 0:
            self.last_signal_time = t
            return "Lot Full"

        # Basic path: decrease by 1
        self.available -= 1
        self.last_signal_time = t

        # A01 / FR07: last spot taken -> Full
        if self.available == 0:
            self.status = "Full"
        return f"{self.available} of {self.total_spots} spots available"


# ---------------------------------------------------------------------------
# SECTION 2: test cases
# ---------------------------------------------------------------------------
results = []


def check(test_id, description, actual, expected):
    passed = actual == expected
    results.append(passed)
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {description}")
    print(f"         expected = {expected!r}   actual = {actual!r}")


def header(title):
    print()
    print("=" * 66)
    print(title)
    print("=" * 66)


def tc01():
    header("TC-01: normal entry decreases the count by 1")
    lot = ParkingLot(lot_id=1, total_spots=120, available=42)
    print(f"  Before: Lot 0001 available = {lot.available}")
    msg = lot.entry(t=0)
    print(f"  Sent 1 entry signal. Display: {msg}")
    check("TC-01", "available spots 42 -> 41", lot.available, 41)
    check("TC-01", "display text", msg, "41 of 120 spots available")
    check("TC-01", "status stays Available", lot.status, "Available")


def tc02():
    header("TC-02: last spot taken -> count 0 and lot marked Full")
    lot = ParkingLot(lot_id=1, total_spots=120, available=1)
    print(f"  Before: Lot 0001 available = {lot.available}")
    lot.entry(t=0)
    print(f"  Sent 1 entry signal. Now available = {lot.available}, status = {lot.status}")
    check("TC-02", "available spots 1 -> 0", lot.available, 0)
    check("TC-02", "status changes to Full", lot.status, "Full")


def tc03():
    header("TC-03: entry at a full lot is rejected")
    lot = ParkingLot(lot_id=1, total_spots=120, available=0)
    print(f"  Before: Lot 0001 available = {lot.available}, status = {lot.status}")
    msg = lot.entry(t=0)
    print(f"  Sent 1 entry signal. Display: {msg}")
    check("TC-03", "'Lot Full' message shown", msg, "Lot Full")
    check("TC-03", "count stays 0 (never negative)", lot.available, 0)
    check("TC-03", "status stays Full", lot.status, "Full")


def tc04():
    header("TC-04: duplicate signal within 2 s is counted once")
    lot = ParkingLot(lot_id=1, total_spots=120, available=42)
    print(f"  Before: Lot 0001 available = {lot.available}")
    lot.entry(t=0)
    msg2 = lot.entry(t=1)  # same car, 1 second later (inside the 2 s window)
    print(f"  Sent signals at t=0s and t=1s. Second signal result: {msg2}")
    check("TC-04", "available spots 42 -> 41 (not 40)", lot.available, 41)
    check("TC-04", "second signal ignored", msg2, "Duplicate ignored")
    check("TC-04", "status stays Available", lot.status, "Available")


if __name__ == "__main__":
    tc01()
    tc02()
    tc03()
    tc04()

    header("SUMMARY")
    passed = sum(results)
    print(f"  {passed} of {len(results)} checks passed")
    print("  OVERALL: " + ("ALL TESTS PASSED" if all(results) else "SOME TESTS FAILED"))