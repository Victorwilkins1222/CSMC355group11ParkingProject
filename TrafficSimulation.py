"""
TrafficSimulation.py

Mock traffic simulator for the Parking System (Group 11).

There are no real cameras, so this generates random "car entered" and
"car left" events and sends them to the database. Only counts are tracked
(no plates, no individual cars) by design.

This file contains NO SQL. All data access goes through a database object
(ParkingDatabase, in sql_lite.py) that must provide these methods:

    get_lot_ids()        -> list[int]
        Every LotID in the database.

    get_lot(lot_id)      -> dict
        The lot's record. Must include the keys "LotName", "TotalSpots"
        and "AvailableSpots" (same names as the database fields).

    car_enters(lot_id)   -> bool
        Lowers AvailableSpots by 1. Returns False (and changes nothing)
        if the lot is already full (AvailableSpots == 0).

    car_leaves(lot_id)   -> bool
        Raises AvailableSpots by 1. Returns False (and changes nothing)
        if the lot is already empty (AvailableSpots == TotalSpots).

Keeping Status ("Available" / "Full") up to date is the database class's job.

Run:  python TrafficSimulation.py
Stop: Ctrl+C
"""

import random
import time
from dataclasses import dataclass
from typing import Optional

from SQL_LITE import ParkingDatabase

# Event types
ENTER = "enter"
LEAVE = "leave"

# Field names used from a lot record (must match the database fields)
FIELD_NAME = "LotName"
FIELD_TOTAL = "TotalSpots"
FIELD_AVAILABLE = "AvailableSpots"


# ---------------------------------------------------------------------------
# Settings: every tunable value lives here
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SimulationConfig:
    min_delay: float = 0.5               # shortest wait between events (seconds)
    max_delay: float = 2.0               # longest wait between events (seconds)
    max_events: Optional[int] = None     # stop after this many events (None = run forever)
    min_enter_chance: float = 0.2        # an entry is never less likely than this...
    max_enter_chance: float = 0.8        # ...or more likely than this


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------
class TrafficSimulation:
    """Generates random car entry/exit events and applies them to the database."""

    def __init__(self, database, config: Optional[SimulationConfig] = None):
        self.database = database
        self.config = config or SimulationConfig()

        self.lot_ids = self.database.get_lot_ids()
        if not self.lot_ids:
            raise ValueError("The database has no lots to simulate.")

    # -- Public API ---------------------------------------------------------
    def run(self):
        """Run until max_events is reached or the user presses Ctrl+C."""
        print("Parking simulation started. Press Ctrl+C to stop.\n")
        events_done = 0

        try:
            while self._should_continue(events_done):
                self._step()
                events_done += 1
                self._wait()
        except KeyboardInterrupt:
            print("\nSimulation stopped.")

    # -- One simulation step ------------------------------------------------
    def _step(self):
        """Generate one random event and apply it."""
        lot_id = self._pick_lot()
        lot = self.database.get_lot(lot_id)

        total = lot[FIELD_TOTAL]
        occupied = total - lot[FIELD_AVAILABLE]

        event = self._pick_event(total, occupied)
        succeeded = self._apply_event(lot_id, event)

        self._report(lot_id, event, succeeded)

    # -- Decision logic (change these to change the behavior) ---------------
    def _pick_lot(self):
        """Choose which lot the next event happens in."""
        return random.choice(self.lot_ids)

    def _pick_event(self, total_spots, occupied):
        """Choose ENTER or LEAVE.

        The fuller the lot, the more likely a car leaves next, so counts
        drift around realistically instead of sticking at empty or full.
        """
        if occupied <= 0:
            return ENTER
        if occupied >= total_spots:
            return LEAVE

        chance_enter = 1 - (occupied / total_spots)
        chance_enter = max(self.config.min_enter_chance,
                           min(chance_enter, self.config.max_enter_chance))
        return ENTER if random.random() < chance_enter else LEAVE

    def _apply_event(self, lot_id, event):
        """Send the event to the database. Returns True if it was accepted."""
        if event == ENTER:
            return self.database.car_enters(lot_id)
        return self.database.car_leaves(lot_id)

    # -- Helpers ------------------------------------------------------------
    def _should_continue(self, events_done):
        max_events = self.config.max_events
        return max_events is None or events_done < max_events

    def _wait(self):
        time.sleep(random.uniform(self.config.min_delay, self.config.max_delay))

    def _report(self, lot_id, event, succeeded):
        """Print what happened and the lot's current availability."""
        lot = self.database.get_lot(lot_id)
        message = self._describe(event, succeeded)
        print(f"[{lot[FIELD_NAME]}] {message:<26} -> "
              f"{lot[FIELD_AVAILABLE]}/{lot[FIELD_TOTAL]} spots available")

    @staticmethod
    def _describe(event, succeeded):
        if event == ENTER:
            return "car entered" if succeeded else "car turned away (full)"
        return "car left" if succeeded else "no car to leave (empty)"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    database = ParkingDatabase()
    simulation = TrafficSimulation(database)
    simulation.run()


if __name__ == "__main__":
    main()