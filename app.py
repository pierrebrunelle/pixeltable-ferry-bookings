"""Ferry Booking API built with Pixeltable.

Two tables (sailings, bookings) declared as Python classes, with the fare, deck class
and booking id as computed columns, served as a REST API by a single FastAPIRouter:
insert, update, delete, compute (quote) and query routes (POST, GET, one-row lookups).

Run locally:
    pxt schema update app.py ferry
    pxt service run app.py ferry

See README.md for the walkthrough and Pixeltable Cloud deployment.
"""
from __future__ import annotations

import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter

TableModel = pxt.model_base()

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
    if not vehicle_len_m:
        return 'foot'
    return 'car' if vehicle_len_m <= 5.5 else 'oversize'


@pxt.udf
def extras_keys(extras: dict | None) -> str:
    """Comma-separated keys of the extras Json, e.g. 'bikes,pets'."""
    return ','.join((extras or {}).keys())


class Sailings(TableModel, name='sailings', has_default_idxs=False):
    sailing_id = pxt.Column(type=pxt.String, primary_key=True)
    route: pxt.String
    depart_at: pxt.String
    vessel: pxt.String
    pax_capacity: pxt.Int

    __indexes__ = [pxt.BtreeIndex(route)]


class Bookings(TableModel, name='bookings', has_default_idxs=False):
    booking_id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    sailing_id: pxt.String
    lead_name: pxt.String
    party_size: pxt.Int
    vehicle_len_m: pxt.Float | None
    extras: pxt.Json | None
    status: pxt.String

    fare = fare_cents(party_size, vehicle_len_m, extras)
    deck_class = deck(vehicle_len_m)
    extras_order = extras_keys(extras)

    __indexes__ = [pxt.BtreeIndex(sailing_id), pxt.BtreeIndex(status)]


@pxt.query
def manifest(sailing_id: str):
    """All bookings on a sailing (index-backed)."""
    return (
        Bookings.where(Bookings.sailing_id == sailing_id)
        .select(Bookings.booking_id, Bookings.lead_name, Bookings.party_size, Bookings.deck_class,
                Bookings.fare, Bookings.status)
        .order_by(Bookings.lead_name)
    )


@pxt.query
def booking_by_lead(lead_name: str):
    """one_row lookup: 0 -> 404, >1 -> 409."""
    return Bookings.where(Bookings.lead_name == lead_name).select(
        Bookings.booking_id, Bookings.sailing_id, Bookings.fare, Bookings.status
    )


@pxt.query
def sailings_on_route(route: str):
    return Sailings.where(Sailings.route == route).select(
        Sailings.sailing_id, Sailings.depart_at, Sailings.vessel, Sailings.pax_capacity
    ).order_by(Sailings.depart_at)


booking_api = FastAPIRouter(name='booking_api')

booking_api.add_insert_route(
    Bookings,
    path='/bookings',
    inputs=[Bookings.sailing_id, Bookings.lead_name, Bookings.party_size, Bookings.vehicle_len_m,
            Bookings.extras, Bookings.status],
    outputs=[Bookings.booking_id, Bookings.fare, Bookings.deck_class, Bookings.extras, Bookings.extras_order],
)
booking_api.add_update_route(
    Bookings,
    path='/bookings/update',
    inputs=[Bookings.status, Bookings.party_size],
    outputs=[Bookings.booking_id, Bookings.status, Bookings.party_size, Bookings.fare],
)
booking_api.add_delete_route(Bookings, path='/bookings/cancel')
booking_api.add_compute_route(
    Bookings,
    path='/quote',
    inputs=[Bookings.party_size, Bookings.vehicle_len_m, Bookings.extras],
    outputs=[Bookings.fare, Bookings.deck_class],
)
booking_api.add_query_route(path='/manifest', query=manifest)
booking_api.add_query_route(path='/manifest-get', query=manifest, method='get')
booking_api.add_query_route(path='/booking/by-lead', query=booking_by_lead, one_row=True, method='get')
booking_api.add_query_route(path='/sailings', query=sailings_on_route, method='get')
booking_api.add_compute_route(Bookings, path='/quote-v2', inputs=[Bookings.party_size, Bookings.vehicle_len_m], outputs=[Bookings.fare])
