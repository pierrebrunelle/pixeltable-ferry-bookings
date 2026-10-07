"""Tables for the ferry booking API, declared as Python classes on a Pixeltable model base."""
import pixeltable as pxt
import pixeltable.functions as pxtf

from udfs import deck, extras_keys, fare_cents

TableModel = pxt.model_base()


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

    # computed columns: evaluated on insert/update, recomputed when inputs change
    fare = fare_cents(party_size, vehicle_len_m, extras)
    deck_class = deck(vehicle_len_m)
    extras_order = extras_keys(extras)

    __indexes__ = [pxt.BtreeIndex(sailing_id), pxt.BtreeIndex(status)]
