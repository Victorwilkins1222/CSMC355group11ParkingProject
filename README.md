# Parking System

**Group 11** · Fundamentals of Software Engineering · VCU

A web-based application that helps drivers find parking in a parking structure. An interactive map shows each lot as a pin with its location and how many spots are currently open. Behind the map, the system counts cars entering and leaving and keeps each lot's available-spot count up to date.

## Why

In Richmond (RVA), drivers heading downtown, to VCU, or to events often circle parking structures without knowing whether any spaces are open. That wastes time and adds to congestion and emissions. This project lets drivers see which lots have open spaces, and how many, before they arrive.

**Intended users:** commuters, students, and visitors looking for parking.
**Other stakeholders:** parking lot operators (better space utilization) and the surrounding community (less congestion).

## Features (Functional Requirements)

| ID | Requirement |
|----|-------------|
| FR01 | Count cars entering the structure and decrease the available spot count |
| FR02 | User can navigate the interactive map |
| FR03 | Pins on the map can be selected to view more information |
| FR04 | Each lot retrieves its information (e.g., availability) from the project's provided data |
| FR05 | Count cars leaving the structure and increase the available spot count |
| FR06 | Display available spots per lot and update after every entry or exit |
| FR07 | Mark a lot as "Full" when available spots reach 0 |

## Quality Requirements (Non-Functional)

| ID | Requirement |
|----|-------------|
| NFR01 | Works on any device |
| NFR02 | Spot tracking is 100% accurate |
| NFR03 | Under 100 ms latency |
| NFR04 | Available 24/7 |
| NFR05 | A first-time user can find a lot and view its availability without training |
| NFR06 | No personal information about drivers or vehicles is collected or stored |

## Use Cases Implemented This Semester

- **UC01 — Count Cars Entering the Parking Structure** (FR01): the entry sensor triggers, the count drops by 1, and the display updates. At 1 spot the lot becomes "Full"; at 0 the entry is rejected with a "Lot Full" message. Duplicate signals within 2 seconds are ignored; the count never goes below 0.
- **UC02 — User Navigates Through the Interactive Map** (FR02): pan and zoom the map, select a lot pin, and view basic info. Handles lots outside the visible area, map load errors, and unavailable lot info.
- **UC03 — User Views Parking Lot Availability** (FR03/FR06): selecting a pin shows e.g. "42 of 120 spots available", or "Full". The count refreshes live while the panel is open.

## Data Model

| Field | Type | Notes |
|-------|------|-------|
| LotID | Integer (4) | Mask `0000` |
| LotName | String (50) | Free text |
| Latitude / Longitude | Decimal | Pin position |
| TotalSpots | Integer (4) | |
| AvailableSpots | Integer (4) | Always between 0 and TotalSpots |
| Status | String | `Available` / `Full` |

**Privacy:** the system tracks only spot availability. It never records license plates or any vehicle or driver information.

## Testing

Sprint 1 test cases cover UC01: normal entry (42 → 41), last spot taken (1 → 0, "Full"), entry at a full lot (stays 0, "Lot Full" message), and a duplicate sensor signal (counted once). See `Group11_TestCases.pdf`.

## Tech Stack

_TBD — fill in once the team decides (backend, frontend/map library, data storage)._

## Getting Started

_TBD — add install and run instructions here._

```bash
# example
git clone <repo-url>
cd parking-system
# install dependencies, then start the app
```

## Team

- Hao La
- Victor Wilkins
- Chris Merino
- Faris Ibrahim Ali
- Ibrahim Shahid
- Kevin Owusu
