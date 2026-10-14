"""Campus shuttle timetable and fleet tracker.

Logs passenger counts per trip, works out average loads, flags under-used
routes and syncs the fleet data to ``fleet.json``.
"""
import json
import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)

# Global state
routes = {"R1": {"name": "Main Gate - Library", "trips": []},
          "R2": {"name": "Hostel - Sports Complex", "trips": []},
          "R3": {"name": "Admin Block - Metro", "trips": []}}
MIN_CAPACITY = 10


def _require_route(route_id):
    """Raise KeyError with a clear message if route_id is not known."""
    if route_id not in routes:
        raise KeyError(f"Unknown route: {route_id}")


def add_trip_log(route_id, passenger_count, logs=None):
    """Record a trip's passenger count and append a line to the log list.

    Raises KeyError for an unknown route and ValueError if passenger_count
    is not a non-negative integer.
    """
    if logs is None:
        logs = []
    _require_route(route_id)
    if (isinstance(passenger_count, bool)
            or not isinstance(passenger_count, int)
            or passenger_count < 0):
        raise ValueError(
            f"Invalid passenger count for {route_id}: {passenger_count!r}")
    routes[route_id]["trips"].append(passenger_count)
    logs.append(f"{datetime.now()}: {route_id} carried {passenger_count}")
    return logs


def remove_route(route_id):
    """Remove a route. Raises KeyError if it does not exist."""
    _require_route(route_id)
    del routes[route_id]


def average_load(route_id):
    """Return the average passengers per trip for a route.

    Raises KeyError for an unknown route and ValueError if it has no trips.
    """
    _require_route(route_id)
    trips = routes[route_id]["trips"]
    if not trips:
        raise ValueError(f"No trips logged for {route_id}")
    return sum(trips) / len(trips)


def underused_routes():
    """Return the ids of routes whose average load is below MIN_CAPACITY.

    Routes with no trips have no average and are skipped (and logged).
    """
    flagged = []
    for route_id in routes:
        try:
            if average_load(route_id) < MIN_CAPACITY:
                flagged.append(route_id)
        except ValueError as err:
            logger.warning("Skipping route in under-use check: %s", err)
    return flagged


def assign_driver(route_id):
    """Pick a driver at random for an existing route."""
    _require_route(route_id)
    drivers = ["Prakash", "Leela", "Imran", "Tom"]
    return random.choice(drivers)


def sync_fleet_data(file="fleet.json"):
    """Write the fleet data to a JSON file, then reload it from that file."""
    with open(file, "w", encoding="utf-8") as out_file:
        json.dump(routes, out_file)
    with open(file, encoding="utf-8") as in_file:
        loaded = json.load(in_file)
    routes.clear()
    routes.update(loaded)


def main():
    """Run the shuttle tracker demo."""
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s: %(message)s")
    sample_trips = [("R1", 32), ("R1", 28), ("R2", 4), ("R2", -6),
                    ("R3", "full")]
    for route_id, count in sample_trips:
        try:
            add_trip_log(route_id, count)
        except (KeyError, ValueError) as err:
            logger.warning("Trip rejected: %s", err.args[0])
    print("Driver for R1:", assign_driver("R1"))
    print("Underused:", underused_routes())
    print("R1 average:", average_load("R1"))
    sync_fleet_data()
    remove_route("R3")
    choice = (input("Route to look up (Enter for R2): ") or "R2")
    choice = choice.strip().upper()
    if choice in routes:
        print("Trips on", choice, ":", routes[choice]["trips"])
    else:
        print("Unknown route:", choice)
    try:
        print("R3 average:", average_load("R3"))
    except (KeyError, ValueError) as err:
        print("R3 average unavailable:", err.args[0])


if __name__ == "__main__":
    main()