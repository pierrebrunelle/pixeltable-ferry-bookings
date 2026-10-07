"""Pixeltable UDFs for the ferry booking API.

UDFs live in their own importable module: Pixeltable records each one by module path
(`udfs.fare_cents`, ...), so the daemon, serving workers and Pixeltable Cloud can import it again.
"""
import pixeltable as pxt

BASE_FARE_CENTS = 2150   # per adult
VEHICLE_CENTS_PER_M = 1375


@pxt.udf
def fare_cents(party_size: int, vehicle_len_m: float | None, extras: dict | None) -> int:
    """Fare: per-person base + vehicle length + priced extras (bikes, pets, cabin)."""
    if party_size is None or party_size < 1:
        raise ValueError(f'party_size must be >= 1, got {party_size}')
    total = BASE_FARE_CENTS * party_size
    if vehicle_len_m:
        total += int(round(vehicle_len_m * VEHICLE_CENTS_PER_M))
    ex = extras or {}
    total += 600 * int(ex.get('bikes', 0) or 0)
    total += 450 * int(ex.get('pets', 0) or 0)
    if ex.get('cabin'):
        total += 4900
    return total


@pxt.udf
def deck(vehicle_len_m: float | None) -> str:
    """Deck class from vehicle length: foot passenger, car, or oversize."""
    if not vehicle_len_m:
        return 'foot'
    return 'car' if vehicle_len_m <= 5.5 else 'oversize'


@pxt.udf
def extras_keys(extras: dict | None) -> str:
    """Comma-separated keys of the extras Json, e.g. 'bikes,pets'."""
    return ','.join((extras or {}).keys())
