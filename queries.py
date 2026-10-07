"""Pixeltable queries (@pxt.query) over the booking tables, exposed as API routes in app.py.

Queries close over the table models, so they sit in their own module next to models.py
(defining them in udfs.py would create a circular import: models -> udfs -> models).
"""
import pixeltable as pxt

from models import Bookings, Sailings


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
    """One-row lookup: 0 rows -> 404, more than one -> 409."""
    return Bookings.where(Bookings.lead_name == lead_name).select(
        Bookings.booking_id, Bookings.sailing_id, Bookings.fare, Bookings.status
    )


@pxt.query
def sailings_on_route(route: str):
    """Sailings on a route, in departure order."""
    return Sailings.where(Sailings.route == route).select(
        Sailings.sailing_id, Sailings.depart_at, Sailings.vessel, Sailings.pax_capacity
    ).order_by(Sailings.depart_at)
