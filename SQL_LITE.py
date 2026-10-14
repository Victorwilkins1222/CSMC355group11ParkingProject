"""
sql_lite.py

SQLite database layer for the Parking System (Group 11).

ParkingDatabase is the only place in the project that contains SQL.
Everything else (the traffic simulation, a future API, a future front end)
talks to the database by calling the methods on this class.

Table: lots
    LotID           INTEGER  unique key
    LotName         TEXT     shown in the pin's info panel
    Latitude        REAL     pin position on the map
    Longitude       REAL     pin position on the map
    TotalSpots      INTEGER  the lot's capacity
    AvailableSpots  INTEGER  live count; always between 0 and TotalSpots
    Status          TEXT     "Available" or "Full" (kept in sync automatically)

Only counts are stored: no plates and no individual cars, by design.
"""

import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
DB_PATH = "parking.db"

STATUS_AVAILABLE = "Available"
STATUS_FULL = "Full"

# Sample lots inserted the first time the database is created, so the
# simulation has something to run against. Replace these with your real
# lots. Format: (LotName, Latitude, Longitude, TotalSpots)
SAMPLE_LOTS = [
    ("Lot A", 37.5485, -77.4527, 50),
    ("Lot B", 37.5492, -77.4510, 30),
    ("Lot C", 37.5478, -77.4541, 20),
]


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
class ParkingDatabase:
    """All reads and writes for parking lot data."""

    def __init__(self, db_path: str = DB_PATH, seed_sample_lots: bool = True):
        self.db_path = db_path
        self._create_table()
        if seed_sample_lots and not self.get_lot_ids():
            self._seed_sample_lots()

    # -- Methods the simulation relies on -----------------------------------
    def get_lot_ids(self) -> List[int]:
        """Return every LotID in the database."""
        with self._connection() as conn:
            rows = conn.execute("SELECT LotID FROM lots ORDER BY LotID").fetchall()
        return [row["LotID"] for row in rows]

    def get_lot(self, lot_id: int) -> Dict:
        """Return one lot's full record as a dict (keys match the table fields).

        Raises ValueError if the lot does not exist.
        """
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM lots WHERE LotID = ?", (lot_id,)
            ).fetchone()
        if row is None:
            raise ValueError(f"No lot with LotID {lot_id}")
        return dict(row)

    def car_enters(self, lot_id: int) -> bool:
        """A car enters: AvailableSpots goes down by 1.

        Returns True if it worked, False if the lot was already full
        (nothing is changed in that case).
        """
        self._require_lot(lot_id)
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE lots
                SET AvailableSpots = AvailableSpots - 1,
                    Status = CASE WHEN AvailableSpots - 1 = 0 THEN ? ELSE ? END
                WHERE LotID = ? AND AvailableSpots > 0
                """,
                (STATUS_FULL, STATUS_AVAILABLE, lot_id),
            )
        return cursor.rowcount == 1

    def car_leaves(self, lot_id: int) -> bool:
        """A car leaves: AvailableSpots goes up by 1.

        Returns True if it worked, False if the lot was already empty
        (nothing is changed in that case).
        """
        self._require_lot(lot_id)
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE lots
                SET AvailableSpots = AvailableSpots + 1,
                    Status = ?
                WHERE LotID = ? AND AvailableSpots < TotalSpots
                """,
                (STATUS_AVAILABLE, lot_id),
            )
        return cursor.rowcount == 1

    # -- Extra methods (not needed by the simulation) -----------------------
    def add_lot(
        self,
        lot_name: str,
        latitude: float,
        longitude: float,
        total_spots: int,
        available_spots: Optional[int] = None,
    ) -> int:
        """Add a new lot and return its LotID. Starts empty unless told otherwise."""
        if available_spots is None:
            available_spots = total_spots
        if not 0 <= available_spots <= total_spots:
            raise ValueError("available_spots must be between 0 and total_spots")

        status = STATUS_FULL if available_spots == 0 else STATUS_AVAILABLE
        with self._connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO lots
                    (LotName, Latitude, Longitude, TotalSpots, AvailableSpots, Status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (lot_name, latitude, longitude, total_spots, available_spots, status),
            )
            return cursor.lastrowid

    def get_all_lots(self) -> List[Dict]:
        """Return every lot's full record (handy for a future API or map page)."""
        with self._connection() as conn:
            rows = conn.execute("SELECT * FROM lots ORDER BY LotID").fetchall()
        return [dict(row) for row in rows]

    def reset_counts(self):
        """Mark every lot as completely empty again."""
        with self._connection() as conn:
            conn.execute(
                "UPDATE lots SET AvailableSpots = TotalSpots, Status = ?",
                (STATUS_AVAILABLE,),
            )

    # -- Internal helpers ---------------------------------------------------
    @contextmanager
    def _connection(self):
        """Open a connection, commit on success, roll back on error, always close."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _create_table(self):
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS lots (
                    LotID          INTEGER PRIMARY KEY AUTOINCREMENT,
                    LotName        TEXT    NOT NULL,
                    Latitude       REAL    NOT NULL,
                    Longitude      REAL    NOT NULL,
                    TotalSpots     INTEGER NOT NULL CHECK (TotalSpots > 0),
                    AvailableSpots INTEGER NOT NULL,
                    Status         TEXT    NOT NULL DEFAULT 'Available',
                    CHECK (AvailableSpots BETWEEN 0 AND TotalSpots)
                )
                """
            )

    def _seed_sample_lots(self):
        for name, latitude, longitude, total_spots in SAMPLE_LOTS:
            self.add_lot(name, latitude, longitude, total_spots)

    def _require_lot(self, lot_id: int):
        """Raise a clear error if lot_id doesn't exist (instead of failing silently)."""
        self.get_lot(lot_id)


# ---------------------------------------------------------------------------
# Quick manual check: python sql_lite.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    db = ParkingDatabase()
    for lot in db.get_all_lots():
        print(lot)